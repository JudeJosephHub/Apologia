"""Intelligence service (ported from Apologia intelligence.py).

Handles sermon chunking, ChromaDB vector search, entity extraction,
knowledge graph building, and course suggestions.
"""

import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from sqlalchemy import delete, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from ..sermons.models import Sermon
from .models import SermonEdge, SermonEntity

logger = logging.getLogger(__name__)


# ── ChromaDB setup ────────────────────────────────────────────────────────

_chroma_client = None
_DATA_DIR = Path("data")
_CHROMA_DIR = _DATA_DIR / "chroma"


def _get_chroma():
    global _chroma_client
    if _chroma_client is None:
        import chromadb
        _CHROMA_DIR.mkdir(parents=True, exist_ok=True)
        _chroma_client = chromadb.PersistentClient(path=str(_CHROMA_DIR))
    return _chroma_client


def _get_collection():
    client = _get_chroma()
    return client.get_or_create_collection(name="sermon_chunks", metadata={"hnsw:space": "cosine"})


# ── Text chunking ────────────────────────────────────────────────────────

def _chunk_text(text: str) -> List[str]:
    if not text or not text.strip():
        return []
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=200, separators=["\n\n", "\n", ". ", " ", ""])
    return splitter.split_text(text)


# ── Scripture reference extraction ────────────────────────────────────────

_BOOKS = (
    r"Genesis|Exodus|Leviticus|Numbers|Deuteronomy|Joshua|Judges|Ruth|"
    r"1\s?Samuel|2\s?Samuel|1\s?Kings|2\s?Kings|1\s?Chronicles|2\s?Chronicles|"
    r"Ezra|Nehemiah|Esther|Job|Psalms?|Proverbs|Ecclesiastes|"
    r"Song\s?of\s?Solomon|Isaiah|Jeremiah|Lamentations|Ezekiel|Daniel|"
    r"Hosea|Joel|Amos|Obadiah|Jonah|Micah|Nahum|Habakkuk|Zephaniah|"
    r"Haggai|Zechariah|Malachi|"
    r"Matthew|Mark|Luke|John|Acts|Romans|"
    r"1\s?Corinthians|2\s?Corinthians|Galatians|Ephesians|Philippians|"
    r"Colossians|1\s?Thessalonians|2\s?Thessalonians|"
    r"1\s?Timothy|2\s?Timothy|Titus|Philemon|Hebrews|James|"
    r"1\s?Peter|2\s?Peter|1\s?John|2\s?John|3\s?John|Jude|Revelation"
)
_SCRIPTURE_RE = re.compile(
    rf"({_BOOKS})\s+(\d{{1,3}})(?::(\d{{1,3}})(?:\s*[-–]\s*(\d{{1,3}}))?)?",
    re.IGNORECASE,
)


def extract_scripture_refs(text: str) -> List[str]:
    refs = []
    for m in _SCRIPTURE_RE.finditer(text):
        book = m.group(1).strip()
        chapter = m.group(2)
        verse_start = m.group(3)
        verse_end = m.group(4)
        if verse_start:
            ref = f"{book} {chapter}:{verse_start}"
            if verse_end:
                ref += f"-{verse_end}"
        else:
            ref = f"{book} {chapter}"
        refs.append(ref)
    return list(dict.fromkeys(refs))


# ── Theological concept extraction ────────────────────────────────────────

_THEOLOGICAL_CONCEPTS = {
    "sovereignty of God": ["sovereign", "sovereignty", "decree", "predestination", "foreordain"],
    "grace": ["grace", "unmerited favor", "mercy of God"],
    "justification": ["justified", "justification", "imputed righteousness", "declared righteous"],
    "sanctification": ["sanctification", "sanctify", "holiness", "holy living", "set apart"],
    "atonement": ["atonement", "propitiation", "expiation", "blood of Christ", "sacrificial death"],
    "redemption": ["redemption", "redeem", "ransom", "bought with a price"],
    "incarnation": ["incarnation", "God became man", "word became flesh", "God in the flesh"],
    "resurrection": ["resurrection", "raised from the dead", "risen Christ", "empty tomb"],
    "eschatology": ["eschatology", "second coming", "end times", "rapture", "millennium", "new heaven"],
    "ecclesiology": ["church", "body of Christ", "bride of Christ", "ecclesiology"],
    "pneumatology": ["Holy Spirit", "Spirit of God", "pneumatology", "Comforter", "Paraclete"],
    "Christology": ["Christ", "Messiah", "Son of God", "Christology", "Logos"],
    "soteriology": ["salvation", "soteriology", "saved", "born again", "new birth"],
    "providence": ["providence", "providential", "God's plan", "divine plan"],
    "sin": ["sin", "depravity", "fallen nature", "original sin", "total depravity"],
    "faith": ["faith", "believe", "trust in God", "sola fide"],
    "repentance": ["repentance", "repent", "turn from sin", "contrition"],
    "prayer": ["prayer", "intercession", "supplication", "communion with God"],
    "worship": ["worship", "praise", "adoration", "glorify God"],
    "covenant": ["covenant", "promise of God", "old covenant", "new covenant"],
}


def extract_theological_concepts(text: str) -> List[str]:
    text_lower = text.lower()
    found = []
    for concept, keywords in _THEOLOGICAL_CONCEPTS.items():
        for kw in keywords:
            if kw.lower() in text_lower:
                found.append(concept)
                break
    return found


# ── Denomination detection ────────────────────────────────────────────────

_DENOMINATIONS = {
    "Reformed": ["reformed", "calvinism", "calvinist", "tulip", "five points"],
    "Methodist": ["methodist", "wesleyan", "arminian", "prevenient grace"],
    "Baptist": ["baptist", "believer's baptism", "baptized believers"],
    "Anglican": ["anglican", "church of england", "episcopal"],
    "Lutheran": ["lutheran", "luther", "augsburg confession"],
    "Presbyterian": ["presbyterian", "westminster confession"],
    "Catholic": ["catholic", "pope", "magisterium", "eucharist"],
    "Pentecostal": ["pentecostal", "charismatic", "speaking in tongues", "gifts of the spirit"],
    "Congregational": ["congregational", "puritan"],
    "Non-denominational": ["non-denominational", "interdenominational"],
}


def detect_traditions(text: str, explicit_denomination: Optional[str] = None) -> List[str]:
    found = []
    if explicit_denomination:
        found.append(explicit_denomination)
    text_lower = text.lower()
    for tradition, keywords in _DENOMINATIONS.items():
        if tradition in found:
            continue
        for kw in keywords:
            if kw in text_lower:
                found.append(tradition)
                break
    return found


# ── Full Intelligence Analysis ────────────────────────────────────────────


def analyze_sermon_intelligence(
    sermon_id: int,
    sermon_name: str,
    content: str,
    preacher: Optional[str] = None,
    themes_json: Optional[str] = None,
    denomination: Optional[str] = None,
) -> Dict[str, Any]:
    themes = []
    if themes_json:
        try:
            themes = json.loads(themes_json) if isinstance(themes_json, str) else themes_json
        except (json.JSONDecodeError, TypeError):
            themes = []

    scripture_refs = extract_scripture_refs(content)
    concepts = extract_theological_concepts(content)
    traditions = detect_traditions(content, denomination)

    chunks = _chunk_text(content)
    collection = _get_collection()

    try:
        existing = collection.get(where={"sermon_id": str(sermon_id)})
        if existing and existing["ids"]:
            collection.delete(ids=existing["ids"])
    except Exception:
        pass

    if chunks:
        chunk_ids = [f"{sermon_id}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [
            {"sermon_id": str(sermon_id), "sermon_name": sermon_name, "pastor_name": preacher or "", "chunk_index": i, "total_chunks": len(chunks)}
            for i in range(len(chunks))
        ]
        collection.add(ids=chunk_ids, documents=chunks, metadatas=metadatas)
        logger.info("Indexed %d chunks for sermon %s", len(chunks), sermon_id)

    return {
        "sermon_id": sermon_id,
        "sermon_name": sermon_name,
        "pastor_name": preacher,
        "themes": themes,
        "scripture_refs": scripture_refs,
        "theological_concepts": concepts,
        "traditions": traditions,
        "chunk_count": len(chunks),
        "indexed_at": datetime.now(timezone.utc).isoformat(),
    }


# ── Semantic search ──────────────────────────────────────────────────────


def search_sermons(query: str, n_results: int = 10) -> List[Dict[str, Any]]:
    collection = _get_collection()
    if collection.count() == 0:
        return []
    results = collection.query(query_texts=[query], n_results=min(n_results, collection.count()))
    hits = []
    if results and results["ids"] and results["ids"][0]:
        for i, doc_id in enumerate(results["ids"][0]):
            hits.append({
                "chunk_id": doc_id,
                "text": results["documents"][0][i] if results["documents"] else "",
                "distance": results["distances"][0][i] if results["distances"] else None,
                "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
            })
    return hits


def find_related_sermons(sermon_id: int, n_results: int = 5) -> List[Dict[str, Any]]:
    collection = _get_collection()
    if collection.count() == 0:
        return []
    try:
        own_chunks = collection.get(where={"sermon_id": str(sermon_id)}, include=["documents"])
    except Exception:
        return []
    if not own_chunks or not own_chunks["documents"]:
        return []

    query_texts = own_chunks["documents"][:3]
    all_scores: Dict[str, List[float]] = {}
    all_names: Dict[str, str] = {}
    all_pastors: Dict[str, str] = {}

    for qt in query_texts:
        results = collection.query(query_texts=[qt], n_results=min(30, collection.count()))
        if not results or not results["ids"] or not results["ids"][0]:
            continue
        for i, chunk_id in enumerate(results["ids"][0]):
            meta = results["metadatas"][0][i] if results["metadatas"] else {}
            sid = meta.get("sermon_id", "")
            if sid == str(sermon_id):
                continue
            distance = results["distances"][0][i] if results["distances"] else 1.0
            similarity = 1.0 - distance
            if sid not in all_scores:
                all_scores[sid] = []
                all_names[sid] = meta.get("sermon_name", "")
                all_pastors[sid] = meta.get("pastor_name", "")
            all_scores[sid].append(similarity)

    related = []
    for sid, scores in all_scores.items():
        avg_sim = sum(scores) / len(scores)
        related.append({
            "sermon_id": int(sid) if sid.isdigit() else sid,
            "sermon_name": all_names[sid],
            "pastor_name": all_pastors[sid],
            "similarity": round(avg_sim, 4),
            "match_count": len(scores),
        })
    related.sort(key=lambda x: x["similarity"], reverse=True)
    return related[:n_results]


# ── Index all sermons ────────────────────────────────────────────────────


async def index_all_sermons(db: AsyncSession) -> Dict[str, Any]:
    result = await db.execute(
        select(Sermon).where(Sermon.transcript != "", Sermon.transcript.isnot(None))
    )
    sermons = result.scalars().all()

    intelligence_results = []
    for s in sermons:
        intel = analyze_sermon_intelligence(
            sermon_id=s.id,
            sermon_name=s.title,
            content=s.transcript,
            preacher=s.preacher,
            themes_json=s.themes,
            denomination=s.denomination,
        )
        intelligence_results.append(intel)

    await _build_knowledge_graph(db, intelligence_results)

    return {
        "indexed": len(intelligence_results),
        "total_chunks": sum(r["chunk_count"] for r in intelligence_results),
        "sermons": [
            {"id": r["sermon_id"], "name": r["sermon_name"], "chunks": r["chunk_count"],
             "scripture_refs": len(r["scripture_refs"]), "concepts": len(r["theological_concepts"])}
            for r in intelligence_results
        ],
    }


# ── Knowledge graph ──────────────────────────────────────────────────────


async def _build_knowledge_graph(db: AsyncSession, intelligence_results: List[Dict[str, Any]]) -> None:
    sermon_ids = [r["sermon_id"] for r in intelligence_results]

    # Clear old entities and edges
    if sermon_ids:
        await db.execute(delete(SermonEntity).where(SermonEntity.sermon_id.in_(sermon_ids)))
        await db.execute(delete(SermonEdge).where(SermonEdge.source_sermon_id.in_(sermon_ids)))

    for intel in intelligence_results:
        sid = intel["sermon_id"]
        entities = []
        for theme in intel.get("themes", []):
            entities.append(SermonEntity(sermon_id=sid, entity_type="theme", entity_value=theme.lower().strip()))
        for ref in intel.get("scripture_refs", []):
            entities.append(SermonEntity(sermon_id=sid, entity_type="scripture", entity_value=ref))
        for concept in intel.get("theological_concepts", []):
            entities.append(SermonEntity(sermon_id=sid, entity_type="concept", entity_value=concept.lower().strip()))
        for tradition in intel.get("traditions", []):
            entities.append(SermonEntity(sermon_id=sid, entity_type="tradition", entity_value=tradition.lower().strip()))
        if intel.get("pastor_name"):
            entities.append(SermonEntity(sermon_id=sid, entity_type="preacher", entity_value=intel["pastor_name"].lower().strip()))
        db.add_all(entities)

    await db.flush()

    # Build edges
    for i, s1_id in enumerate(sermon_ids):
        s1_intel = intelligence_results[i]
        s1_entities = _collect_entity_sets(s1_intel)
        for j in range(i + 1, len(sermon_ids)):
            s2_id = sermon_ids[j]
            s2_intel = intelligence_results[j]
            s2_entities = _collect_entity_sets(s2_intel)
            _compute_edges_in_memory(db, s1_id, s2_id, s1_entities, s2_entities)

    await db.commit()


def _collect_entity_sets(intel: Dict[str, Any]) -> Dict[str, set]:
    sets: Dict[str, set] = {"theme": set(), "scripture": set(), "concept": set(), "tradition": set(), "preacher": set()}
    for t in intel.get("themes", []):
        sets["theme"].add(t.lower().strip())
    for r in intel.get("scripture_refs", []):
        sets["scripture"].add(r)
    for c in intel.get("theological_concepts", []):
        sets["concept"].add(c.lower().strip())
    for tr in intel.get("traditions", []):
        sets["tradition"].add(tr.lower().strip())
    if intel.get("pastor_name"):
        sets["preacher"].add(intel["pastor_name"].lower().strip())
    return sets


def _compute_edges_in_memory(
    db: AsyncSession,
    s1_id: int,
    s2_id: int,
    s1_entities: Dict[str, set],
    s2_entities: Dict[str, set],
) -> None:
    edge_types = {
        "theme": "theme_overlap",
        "scripture": "scripture_overlap",
        "concept": "concept_overlap",
        "preacher": "same_preacher",
        "tradition": "tradition_overlap",
    }
    for entity_type, edge_type in edge_types.items():
        shared_1 = s1_entities.get(entity_type, set())
        shared_2 = s2_entities.get(entity_type, set())
        overlap = shared_1 & shared_2
        if overlap:
            union = shared_1 | shared_2
            weight = len(overlap) / len(union) if union else 0
            db.add(SermonEdge(
                source_sermon_id=s1_id,
                target_sermon_id=s2_id,
                edge_type=edge_type,
                weight=weight,
                shared_data=json.dumps(sorted(overlap)),
            ))


# ── Graph queries ────────────────────────────────────────────────────────


async def get_sermon_graph(db: AsyncSession, sermon_id: int) -> Dict[str, Any]:
    entities_result = await db.execute(
        select(SermonEntity).where(SermonEntity.sermon_id == sermon_id)
    )
    entities = entities_result.scalars().all()
    entity_map: Dict[str, List[str]] = {}
    for e in entities:
        entity_map.setdefault(e.entity_type, []).append(e.entity_value)

    edges_result = await db.execute(
        select(SermonEdge).where(
            (SermonEdge.source_sermon_id == sermon_id) | (SermonEdge.target_sermon_id == sermon_id)
        )
    )
    edges = edges_result.scalars().all()

    connections: Dict[int, Dict[str, Any]] = {}
    for edge in edges:
        other_id = edge.target_sermon_id if edge.source_sermon_id == sermon_id else edge.source_sermon_id
        if other_id not in connections:
            connections[other_id] = {"edges": [], "total_weight": 0.0}
        shared = json.loads(edge.shared_data) if edge.shared_data else []
        connections[other_id]["edges"].append({"type": edge.edge_type, "weight": edge.weight, "shared": shared})
        connections[other_id]["total_weight"] += edge.weight

    connected_ids = list(connections.keys())
    connected_sermons = {}
    if connected_ids:
        result = await db.execute(select(Sermon).where(Sermon.id.in_(connected_ids)))
        for s in result.scalars().all():
            connected_sermons[s.id] = {"sermon_name": s.title, "pastor_name": s.preacher}

    related = []
    for other_id, conn_data in connections.items():
        info = connected_sermons.get(other_id, {})
        related.append({
            "sermon_id": other_id,
            "sermon_name": info.get("sermon_name", "Unknown"),
            "pastor_name": info.get("pastor_name"),
            "total_weight": round(conn_data["total_weight"], 4),
            "edges": conn_data["edges"],
        })
    related.sort(key=lambda x: x["total_weight"], reverse=True)

    return {"sermon_id": sermon_id, "entities": entity_map, "related_sermons": related, "edge_count": len(edges)}


async def get_full_graph(db: AsyncSession) -> Dict[str, Any]:
    # Get all sermons that have entities
    entity_sermon_ids = await db.execute(select(SermonEntity.sermon_id).distinct())
    indexed_ids = [row[0] for row in entity_sermon_ids.all()]

    if not indexed_ids:
        return {"nodes": [], "edges": []}

    sermon_result = await db.execute(select(Sermon).where(Sermon.id.in_(indexed_ids)))
    sermons = sermon_result.scalars().all()

    nodes = []
    for s in sermons:
        ent_result = await db.execute(select(SermonEntity).where(SermonEntity.sermon_id == s.id))
        ent_map: Dict[str, List[str]] = {}
        for e in ent_result.scalars().all():
            ent_map.setdefault(e.entity_type, []).append(e.entity_value)
        nodes.append({
            "id": s.id,
            "sermon_name": s.title,
            "pastor_name": s.preacher,
            "denomination": s.denomination,
            "entities": ent_map,
        })

    edge_result = await db.execute(select(SermonEdge))
    edges = []
    for e in edge_result.scalars().all():
        shared = json.loads(e.shared_data) if e.shared_data else []
        edges.append({
            "source": e.source_sermon_id,
            "target": e.target_sermon_id,
            "type": e.edge_type,
            "weight": e.weight,
            "shared": shared,
        })

    return {"nodes": nodes, "edges": edges}


async def explore_entity(db: AsyncSession, entity_type: str, entity_value: str) -> Dict[str, Any]:
    result = await db.execute(
        select(SermonEntity, Sermon)
        .join(Sermon, SermonEntity.sermon_id == Sermon.id)
        .where(SermonEntity.entity_type == entity_type)
        .where(func.lower(SermonEntity.entity_value) == entity_value.lower())
    )
    rows = result.all()
    sermons_list = [
        {"sermon_id": entity.sermon_id, "sermon_name": sermon.title, "pastor_name": sermon.preacher}
        for entity, sermon in rows
    ]
    return {"entity_type": entity_type, "entity_value": entity_value, "sermon_count": len(sermons_list), "sermons": sermons_list}


async def get_all_entities(db: AsyncSession) -> Dict[str, List[str]]:
    result = await db.execute(
        select(SermonEntity.entity_type, SermonEntity.entity_value).distinct()
    )
    entity_map: Dict[str, List[str]] = {}
    for row in result.all():
        entity_map.setdefault(row[0], []).append(row[1])
    return entity_map


async def suggest_course(db: AsyncSession, topic: str, max_sermons: int = 10) -> Dict[str, Any]:
    hits = search_sermons(topic, n_results=max_sermons * 3)
    seen_sermons = {}
    for hit in hits:
        sid = hit["metadata"].get("sermon_id", "")
        if sid and sid not in seen_sermons:
            seen_sermons[sid] = hit

    sermon_ids = [int(sid) if sid.isdigit() else sid for sid in list(seen_sermons.keys())[:max_sermons]]
    if not sermon_ids:
        return {"topic": topic, "sermon_count": 0, "sermons": [], "themes_covered": [], "concepts_covered": [], "scripture_refs": []}

    int_ids = [sid for sid in sermon_ids if isinstance(sid, int)]
    result = await db.execute(select(Sermon).where(Sermon.id.in_(int_ids))) if int_ids else None
    sermon_map = {}
    if result:
        for s in result.scalars().all():
            sermon_map[s.id] = s

    course_sermons = []
    all_themes, all_concepts, all_refs = set(), set(), set()
    for sid in sermon_ids:
        s = sermon_map.get(sid)
        if not s:
            continue
        intel = analyze_sermon_intelligence(s.id, s.title, s.transcript or "", s.preacher, s.themes, s.denomination)
        all_themes.update(intel["themes"])
        all_concepts.update(intel["theological_concepts"])
        all_refs.update(intel["scripture_refs"])
        course_sermons.append({"sermon_id": s.id, "sermon_name": s.title, "pastor_name": s.preacher, "relevance": seen_sermons.get(str(sid), {}).get("distance")})

    return {
        "topic": topic,
        "sermon_count": len(course_sermons),
        "sermons": course_sermons,
        "themes_covered": sorted(all_themes),
        "concepts_covered": sorted(all_concepts),
        "scripture_refs": sorted(all_refs),
    }
