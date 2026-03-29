"""Seed the database with classic public-domain sermons.

Usage:
    cd apps/backend
    python -m scripts.seed_sermons
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from src.core.database import get_engine, get_session_factory
from src.models_base import Base
from src.domains.sermons.models import Sermon, UserSermon  # noqa: F401
from src.domains.profiles.models import Profile  # noqa: F401
from src.domains.scriptures.models import Scripture, SermonScripture  # noqa: F401
from src.domains.links.models import SermonLink  # noqa: F401
from src.domains.courses.models import Course, CourseModule  # noqa: F401

# ─── Classic Public-Domain Sermons ──────────────────────────────────────────
# These are real historical sermons whose texts are in the public domain.

SERMONS = [
    {
        "title": "Sinners in the Hands of an Angry God",
        "preacher": "Jonathan Edwards",
        "date_preached": "1741-07-08",
        "denomination": "Congregational",
        "source_url": "https://www.gutenberg.org/ebooks/34632",
        "themes": '["judgment", "hell", "repentance", "sovereignty of God", "Great Awakening"]',
        "summary": "Edwards' most famous sermon, delivered during the Great Awakening in Enfield, Connecticut. Using vivid imagery, he urges listeners to recognize their precarious spiritual state and the imminence of divine judgment, calling them to repentance. The sermon's central metaphor — a spider dangled over a flame — remains one of the most powerful images in American religious literature.",
        "outline": "I. God's wrath against sinners\nII. The precariousness of the unconverted state\nIII. Nothing keeps wicked men out of hell but the mere pleasure of God\nIV. Application and call to repentance",
        "transcript": "Their foot shall slide in due time (Deuteronomy 32:35). In this verse is threatened the vengeance of God on the wicked unbelieving Israelites, who were God's visible people, and who lived under the means of grace; but who, notwithstanding all God's wonderful works towards them, remained void of counsel, having no understanding in them. Under all the cultivations of heaven, they brought forth bitter and poisonous fruit.\n\nThe expression I have chosen for my text, 'Their foot shall slide in due time,' seems to imply the following things, relating to the punishment and destruction to which these wicked Israelites were exposed.\n\nThat they were always exposed to destruction; as one that stands or walks in slippery places is always exposed to fall. This is implied in the manner of their destruction coming upon them, being represented by their foot sliding. The same is expressed, Psalm 73:18. 'Surely thou didst set them in slippery places; thou castedst them down into destruction.'\n\nIt implies, that they were always exposed to sudden unexpected destruction. As he that walks in slippery places is every moment liable to fall, he cannot foresee one moment whether he shall stand or fall the next; and when he does fall, he falls at once without warning.\n\nAnother thing implied is, that they are liable to fall of themselves, without being thrown down by the hand of another; as he that stands or walks on slippery ground needs nothing but his own weight to throw him down.\n\nThat the reason why they are not fallen already, and do not fall now, is only that God's appointed time is not come. For it is said, that when that due time, or appointed time comes, their foot shall slide. Then they shall be left to fall, as they are inclined by their own weight. God will not hold them up in these slippery places any longer, but will let them go; and then, at that very instant, they shall fall into destruction; as he that stands on such slippery declining ground, on the edge of a pit, he cannot stand alone, when he is let go he immediately falls and is lost.\n\nThe observation from the words that I would now insist upon is this: There is nothing that keeps wicked men at any one moment out of hell, but the mere pleasure of God.",
        "status": "published",
    },
    {
        "title": "The New Birth",
        "preacher": "George Whitefield",
        "date_preached": "1737-01-01",
        "denomination": "Methodist/Anglican",
        "source_url": "https://www.gutenberg.org/ebooks/author/4665",
        "themes": '["regeneration", "new birth", "salvation", "John 3", "Holy Spirit"]',
        "summary": "George Whitefield preaches on the necessity of the new birth from John 3:7 — 'Ye must be born again.' He argues that moral reformation alone is insufficient and that every person needs a supernatural transformation by the Holy Spirit. The sermon systematically addresses different classes of people — the moralist, the formalist, and the careless — showing each their need for regeneration.",
        "outline": "I. What is meant by the new birth\nII. Why we must be born again\nIII. How this new birth is wrought in the soul\nIV. Directions for seeking the new birth",
        "transcript": "If we look into the writings of the Old Testament, we shall find that the doctrine of the new birth is not a new doctrine, but what was taught by Moses and the prophets. Marvel not that I said unto thee, Ye must be born again. For no sooner had our first parents fallen from the state of original righteousness, but God promised that the seed of the woman should bruise the serpent's head.\n\nBut notwithstanding, so many plain texts of scripture can be produced to prove this doctrine, yet if we look into the world, we shall find that the greatest part of mankind either live in open opposition to, or at best are but almost persuaded to be real Christians. And this is one of the reasons why I chose to insist upon it, because it is a subject so very important.\n\nFirst then, by the new birth, we are to understand, being born of the Spirit. Nicodemus, being a master in Israel, may well wonder at this doctrine, for it is a great mystery. That which is born of the flesh is flesh, and that which is born of the Spirit is spirit. As in our natural birth we are born of earthly parents, so in our spiritual birth we are born of the Spirit.\n\nBut why must we be born again? The necessity of the new birth appears from this: we are all by nature in a state of spiritual death. By Adam's fall, we lost our original righteousness and holiness, and came into this world with a corrupt nature, prone to evil. There is in all unregenerate persons a blindness of the understanding. The things of the Spirit of God are foolishness unto the natural man. There is likewise a perverseness of the will: we naturally choose darkness rather than light, evil rather than good.\n\nHow then is this new birth wrought? It is wrought by the Spirit of God, through the instrumentality of the Word. Faith cometh by hearing, and hearing by the Word of God. The Spirit applies the Word effectually to the heart, convinces the sinner of his sin, gives him a new heart and a new spirit, creates in him clean desires, and enables him to walk in newness of life.",
        "status": "published",
    },
    {
        "title": "The Immutability of God",
        "preacher": "Charles H. Spurgeon",
        "date_preached": "1855-01-07",
        "denomination": "Baptist",
        "source_url": "https://www.spurgeon.org/resource-library/sermons/the-immutability-of-god/",
        "themes": '["God\'s nature", "immutability", "attributes of God", "comfort", "theology proper"]',
        "summary": "Delivered at New Park Street Chapel when Spurgeon was only 20 years old, this sermon expounds on Malachi 3:6 — 'For I am the Lord, I change not.' Spurgeon presents God's unchangeableness as a source of deep comfort for believers and solemn warning for the unrepentant. He examines God's immutability in His essence, attributes, plans, and promises.",
        "outline": "I. God is unchangeable in His essence\nII. God is unchangeable in His attributes\nIII. God is unchangeable in His plans and purposes\nIV. God is unchangeable in His promises\nV. Practical applications for comfort and warning",
        "transcript": "For I am the Lord, I change not; therefore ye sons of Jacob are not consumed (Malachi 3:6). It has been said that the proper study of mankind is man. I believe it is equally true that the proper study of God's elect is God. The highest science, the loftiest speculation, the mightiest philosophy which can ever engage the attention of a child of God, is the name, the nature, the person, the work, the doings, and the existence of the great God whom he calls his Father.\n\nThere is something exceedingly improving to the mind in a contemplation of the Divinity. It is a subject so vast, that all our thoughts are lost in its immensity; so deep, that our pride is drowned in its infinity. Other subjects we can compass and grapple with; in them we feel a kind of self-content, and go our way with the thought, 'Behold I am wise.' But when we come to this master-science, finding that our plumb-line cannot sound its depth, and that our eagle eye cannot see its height, we turn away with the thought, 'I am but of yesterday, and know nothing.'\n\nI know nothing more fitted to calm the surging billow of sorrow and trial than a devout musing upon the subject of God's immutability. It is a pillow upon which the Christian has often laid his head. It has been a sure anchor in the time of flood and storm.\n\nFirst, I shall speak of God's immutability in His essence. Secondly, in His attributes. Thirdly, in His plans. And fourthly, in His promises.\n\nGod is unchangeable in His essence. The nature of God cannot be changed. He is the same God now as when He walked in the garden of Eden at the cool of the day. He is the same God whom Abraham worshipped when he left his father's house. The same yesterday, today, and forever. Man changes — the world changes — but God changes never.",
        "status": "published",
    },
    {
        "title": "All of Grace",
        "preacher": "Charles H. Spurgeon",
        "date_preached": "1886-01-01",
        "denomination": "Baptist",
        "source_url": "https://www.gutenberg.org/ebooks/22143",
        "themes": '["grace", "salvation", "faith", "free will", "gospel invitation"]',
        "summary": "One of Spurgeon's most beloved works, 'All of Grace' is an earnest appeal to the unconverted. He presents the gospel in its simplest terms — that salvation is entirely by God's grace, received through faith alone. The work covers the nature of saving faith, the freeness of grace, and practical encouragements for those seeking salvation.",
        "outline": "I. To you — the personal gospel invitation\nII. What is saving faith?\nIII. How may faith be illustrated?\nIV. Why are we saved by faith?\nV. The increase of faith\nVI. The obedience of faith",
        "transcript": "The Lord, who is the fountain of all mercy, seems in His infinite grace to delight in the pardon of transgressors. He has given His only-begotten Son for this very purpose, that whosoever believeth in Him should not perish, but should have eternal life. This is a faithful saying, and worthy of all acceptation, that Christ Jesus came into the world to save sinners.\n\nI thought it well to write to you, dear reader, a short word of simple instruction, by which those who are willing to be guided may be led into the way of life. This little book is sent forth in the hope that it may lead some of those who are inquiring for the way of salvation into the peace and rest which come from a true acceptance of the grace of God.\n\nTo you, whoever you may be — to you who have no hopeful sign or good feeling, no recommendation of fitness — to you, as a sinner, God's free grace is now presented.\n\nWhat is this faith? It is not a blind, unreasoning assent to the things which are contained in the Bible. It is not the faith of tradition, received because your father believed it. It is the heart's trust in Christ as the one Savior. It is laying hold upon Christ as Christ, and trusting Him with all the weight and care of the soul.\n\nWhy does God save by faith? Because faith is the giving up of all claim to merit. Faith is the reception of God's free gift. Faith gives glory to God, because it is the eye which looks to Him, the hand which receives from Him, the mouth which feeds upon Him. God saves by faith because in so doing all the glory goes to Him, and none remains for man.",
        "status": "published",
    },
    {
        "title": "A Divine and Supernatural Light",
        "preacher": "Jonathan Edwards",
        "date_preached": "1734-01-01",
        "denomination": "Congregational",
        "source_url": "https://www.gutenberg.org/ebooks/34632",
        "themes": '["illumination", "Holy Spirit", "spiritual knowledge", "conversion", "epistemology"]',
        "summary": "Edwards distinguishes between two kinds of knowledge: mere notional understanding of religious truths and the spiritual 'sense of the heart' that comes only through the Holy Spirit's work. He argues that true spiritual knowledge involves not just knowing that God is holy, but having a direct sense of the loveliness and beauty of that holiness. This sermon laid the philosophical groundwork for much of Reformed epistemology.",
        "outline": "I. What this spiritual light is not\nII. What this spiritual light is — a true sense of divine excellency\nIII. How this light is given immediately by God\nIV. Why it is rational to suppose this light is given",
        "transcript": "And Jesus answered and said unto him, Blessed art thou, Simon Bar-Jonah: for flesh and blood hath not revealed it unto thee, but my Father which is in heaven (Matthew 16:17). Christ addresses these words to Peter upon occasion of his professing his faith in Him as the Son of God.\n\nThere is such a thing as a spiritual and divine light, immediately imparted to the soul by God, of a different nature from any that is obtained by natural means. In what I say on this subject, I would show: first, what this divine light is; second, how it is given immediately by God and not obtained by natural means; and third, show the truth of the doctrine.\n\nFirst, I would show what this divine light is. And it may be described by the following things: this spiritual light is not the suggesting of any new truths or propositions not already contained in the Word of God. It does not teach anyone new doctrines. It does not suggest to the understanding any new proposition.\n\nWhat this light is may be thus explained: there is a difference between having an opinion that God is holy and gracious, and having a sense of the loveliness and beauty of that holiness and grace. There is a difference between having a rational judgment that honey is sweet, and having a sense of its sweetness. A man may have the former who has never tasted honey.\n\nSo there is a difference between believing that a person is beautiful, and seeing their beauty. The former may be obtained by hearsay, but the latter only by seeing the countenance. Thus there is a vast difference between having a judgment that the things of religion are true and excellent, and having a sense of their beauty and sweetness. The former may be the result of speculation; the latter is the work of the Spirit of God upon the heart.",
        "status": "published",
    },
    {
        "title": "The Free Grace of God",
        "preacher": "John Wesley",
        "date_preached": "1740-01-01",
        "denomination": "Methodist",
        "source_url": "https://www.gutenberg.org/ebooks/author/2632",
        "themes": '["grace", "free will", "predestination", "Arminianism", "universal atonement"]',
        "summary": "Wesley's influential sermon on Romans 8:32 — 'He that spared not His own Son, but delivered Him up for us all, how shall He not with Him also freely give us all things?' Wesley argues that God's grace is freely available to all people, not limited to a predetermined elect. He emphasizes the universality of Christ's atonement while maintaining that each person must freely respond to grace.",
        "outline": "I. The gift of God's Son for all\nII. The freeness of God's grace\nIII. The extent of God's grace — to all people\nIV. Objections answered\nV. Practical exhortations",
        "transcript": "How freely does God love the world! While we were yet sinners, Christ died for us. He that spared not His own Son, but delivered Him up for us all, how shall He not with Him also freely give us all things? He that did not withhold His only-begotten, what good thing will He withhold from those who love Him?\n\nThe grace of God which bringeth salvation hath appeared to all men. Not to a select few, not to a chosen number who were predestinated from before the foundation of the world, but to ALL men. The love of God is wider than the measure of man's mind, and the heart of the Eternal is most wonderfully kind.\n\nThere is a free gift come upon all men unto justification of life. All have sinned, and come short of the glory of God, being justified freely by His grace through the redemption that is in Christ Jesus. Freely! Not by our works, not by our merits, not by our deservings, but freely — by His grace alone.\n\nHe tasted death for every man. He gave Himself a ransom for all. He is the propitiation for our sins, and not for ours only, but also for the sins of the whole world. How then can we narrow the grace of God? How can we limit the Holy One of Israel? Let us open wide our hearts to receive the free grace which He so freely offers.",
        "status": "published",
    },
    {
        "title": "The Almost Christian",
        "preacher": "George Whitefield",
        "date_preached": "1739-01-01",
        "denomination": "Methodist/Anglican",
        "source_url": "https://www.gutenberg.org/ebooks/author/4665",
        "themes": '["conviction", "nominal Christianity", "self-examination", "true conversion", "Acts 26:28"]',
        "summary": "Whitefield's searching sermon on Acts 26:28 — 'Almost thou persuadest me to be a Christian.' He defines two categories: the 'almost' Christian who has outward religion but no inward transformation, and the 'altogether' Christian who has experienced genuine conversion. The sermon challenges listeners to examine whether their faith is genuine or merely formal.",
        "outline": "I. What is meant by an 'almost' Christian\nII. What is meant by an 'altogether' Christian\nIII. Several reasons why so many are no more than 'almost' Christians\nIV. A word of exhortation",
        "transcript": "King Agrippa, almost thou persuadest me to be a Christian (Acts 26:28). The chapter out of which the text is taken contains an admirable apology made by the Apostle Paul before King Agrippa when he was called to answer for the hope that was in him.\n\nThe word 'almost' rises up in judgment against many. Almost — but lost. Almost — but not altogether. How many pass through life, hearing the Word of God, agreeing to its truth, feeling its power, trembling under its warnings, and yet — only almost Christians.\n\nWhat is meant by an 'almost' Christian? First, an almost Christian, if we consider him in respect of his duty to God, is one that halts between two opinions; that wavers between Christ and the world. He is sometimes moved to follow good counsel, but then worldly thoughts intervene. He is almost persuaded to leave his faults, but habitually returns to them.\n\nAn almost Christian is one who is fond of the form of godliness but afraid of the power of it. He goes to church, says his prayers, attends the outward means of grace, and appears fair in the eyes of men, but there his religion ends. He stops short of a thorough, radical change of heart.\n\nWhat then is an altogether Christian? He is one that is in Christ a new creature. Old things are passed away, behold all things are become new. He not only avoids outward sins but cleanses himself from all filthiness of both flesh and spirit. He does not merely talk about religion — he lives it. He is not content with having on the form — he has also the power of godliness.",
        "status": "published",
    },
    {
        "title": "Justification by Faith",
        "preacher": "John Wesley",
        "date_preached": "1746-01-01",
        "denomination": "Methodist",
        "source_url": "https://www.gutenberg.org/ebooks/author/2632",
        "themes": '["justification", "faith alone", "Romans", "soteriology", "imputation"]',
        "summary": "Wesley's systematic exposition of justification by faith from Romans 4:5 — 'To him that worketh not, but believeth on Him that justifieth the ungodly, his faith is counted for righteousness.' Wesley carefully defines justification as God's pardoning and accepting the sinner, distinguishing it from sanctification. He explains the ground (Christ's atonement), the condition (faith), and the fruits of justification.",
        "outline": "I. The general ground of justification — the necessity arises from the fall\nII. What justification is — pardon, the forgiveness of sins\nIII. Who are the justified — the ungodly\nIV. On what terms — by faith alone",
        "transcript": "To him that worketh not, but believeth on Him that justifieth the ungodly, his faith is counted for righteousness (Romans 4:5). To him that worketh not — How clearly does the apostle here express the whole of what was spoken before! Him that worketh not means him who neither has any true righteousness of his own, nor pretends to any; who comes to God as a mere sinner, ungodly, lost, deserving nothing.\n\nWhat then is justification? It is not being made righteous in a moral or ethical sense. It is not sanctification. Justification is God's act of declaring the sinner righteous on account of the atoning work of Christ received by faith. It is a judicial act of God the Father, pronouncing the believing sinner forgiven and accepted.\n\nWho are the justified? The ungodly! This is the wonder of the gospel. Not the righteous, not the deserving, not the moralists or the law-keepers, but sinners. God justifieth the ungodly. This is the scandal of grace — that a holy God declares unholy men righteous, not on the basis of their character but on the basis of Christ's finished work.\n\nOn what condition are we justified? By faith alone. Not by the works of the law, for by the deeds of the law shall no flesh be justified. Not by our own obedience, however sincere. But faith — trust — casting ourselves wholly upon the mercy of God in Christ.\n\nFaith has no merit in itself. It is not the virtue of faith that saves us. Rather, faith is the hand that receives the gift. Faith is the eye that looks to Christ. Faith is the foot that runs to the refuge. The whole worth is in the object of faith — Christ Jesus — not in the act of believing itself.",
        "status": "published",
    },
    {
        "title": "Compel Them to Come In",
        "preacher": "Charles H. Spurgeon",
        "date_preached": "1858-12-05",
        "denomination": "Baptist",
        "source_url": "https://www.spurgeon.org/resource-library/sermons/compel-them-to-come-in/",
        "themes": '["evangelism", "gospel invitation", "Luke 14", "great supper parable", "urgency"]',
        "summary": "Spurgeon passionately calls sinners to come to Christ based on the Parable of the Great Supper in Luke 14:23 — 'Compel them to come in.' He argues for the urgency and earnestness of gospel proclamation, addressing reason, conscience, and the emotions as he pleads with the lost. This sermon is a masterclass in evangelistic preaching.",
        "outline": "I. The great supper — what God has prepared\nII. The excuses of the invited\nIII. The command to compel — gospel urgency\nIV. The means of compelling — earnest persuasion\nV. Direct address to the unconverted",
        "transcript": "And the Lord said unto the servant, Go out into the highways and hedges, and compel them to come in, that my house may be filled (Luke 14:23). This is the Royal Mandate — the command of the King of kings. Not simply to invite, but to compel. There is a holy compulsion in the gospel which respects the free will of man yet presses upon him with divine urgency.\n\nA great supper had been prepared, and the invited guests made excuse. One had bought a piece of ground. Another had purchased five yoke of oxen. A third had married a wife. Each had his reason; none had a sufficient one. Do you not see in this a picture of the present age? The feast of the gospel is spread, yet men turn away for the most trivial causes.\n\nAnd now the Master commands: Compel them to come in! Not by force of arm, not by persecution, but by the force of love, by earnest persuasion, by warm entreaty, by solemn argument, by tender appeal. Compel them by telling them of the feast that is prepared. Compel them by describing the wrath to come. Compel them by showing them the wounds of Christ. Compel them by weeping over their souls as Jesus wept over Jerusalem.\n\nI would now address the outsiders — those in the highways and hedges. You who think yourselves too bad, too far gone, too unworthy — it is you whom I am commanded to bring in. The very publicans and harlots enter the kingdom of God before the self-righteous Pharisees. Come as you are. Come now. The supper is ready, and there is room. The Master's house must be filled.",
        "status": "published",
    },
    {
        "title": "The Sovereignty of God in Salvation",
        "preacher": "D.L. Moody",
        "date_preached": "1877-01-01",
        "denomination": "Evangelical",
        "source_url": "https://www.gutenberg.org/ebooks/author/3066",
        "themes": '["sovereignty", "salvation", "evangelism", "God\'s power", "Moody revivals"]',
        "summary": "D.L. Moody, the great 19th-century evangelist, preaches on God's sovereign power in bringing about salvation. Despite being known primarily as an evangelist who emphasized human decision, Moody here highlights God's initiating role in salvation, showing that conviction, conversion, and perseverance all depend on divine power working through the gospel.",
        "outline": "I. God's sovereign choice to save sinners\nII. The power of the gospel to transform lives\nIII. Stories from revival meetings\nIV. The sinner's response to God's initiative\nV. Final appeal",
        "transcript": "I want to talk to you tonight about the power of God in salvation. I have traveled across this country and across the sea, and everywhere I have gone, I have seen one thing proven again and again: that when God sets His love upon a sinner, nothing in heaven or earth can prevent that sinner from being saved.\n\nI have stood in great halls and watched hardened men weep under the preaching of the gospel. I have seen drunkards come forward and lay down their bottles. I have seen gamblers confess their sins. Not because of eloquent preaching — heaven knows I am no orator — but because the power of God was present to save.\n\nFriends, it is not by might, nor by power, but by the Spirit of the Lord. We may preach until our tongues are tied. We may argue until our voices fail. But unless the Spirit of God takes the truth and drives it into the heart, all our efforts are in vain.\n\nBut when God moves — oh, when God moves! — then the mountains melt like wax. The hardest heart breaks. The proudest knee bows. The most resistant will yields. I have seen it a thousand times, and I expect to see it a thousand more.\n\nGod is sovereign in salvation. He chooses to use the foolishness of preaching to save them that believe. He condescends to use men of dust and weakness as His instruments. But the power is His and His alone. And I say to every sinner in this hall tonight: God is able to save you, and He is willing to save you, and if you will but come to Christ in simple faith, He will save you this very hour.",
        "status": "published",
    },
    {
        "title": "The Weight of Glory",
        "preacher": "C.S. Lewis",
        "date_preached": "1941-06-08",
        "denomination": "Anglican",
        "source_url": "https://www.wheaton.edu/academics/programs/c-s-lewis/",
        "themes": '["heaven", "glory", "desire", "longing", "eternal perspective", "neighbor love"]',
        "summary": "Delivered at the Church of St Mary the Virgin, Oxford, Lewis reflects on the Christian hope of glory. He argues that our deepest desires — for beauty, for home, for something we cannot name — are actually pointers to heaven. Lewis famously states that we are 'half-hearted creatures, fooling about with drink and sex and ambition when infinite joy is offered us.' He concludes with the staggering weight of the potential glory in every person we meet.",
        "outline": "I. The problem with unselfishness vs. the biblical promise of reward\nII. The nature of our deepest desires\nIII. The promise of glory — to be noticed by God\nIV. The weight of glory in our neighbor\nV. Responsibility toward one another's eternal destiny",
        "transcript": "If you asked twenty good men to-day what they thought the highest of the virtues, nineteen of them would reply, Unselfishness. But if you asked almost any of the great Christians of old he would have replied, Love. You see what has happened? A negative term has been substituted for a positive.\n\nThe New Testament has lots to say about self-denial, but not about self-denial as an end in itself. We are told to deny ourselves and to take up our crosses in order that we may follow Christ; and nearly every description of what we shall ultimately find if we do so contains an appeal to desire.\n\nIndeed, if we consider the unblushing promises of reward and the staggering nature of the rewards promised in the Gospels, it would seem that Our Lord finds our desires not too strong, but too weak. We are half-hearted creatures, fooling about with drink and sex and ambition when infinite joy is offered us, like an ignorant child who wants to go on making mud pies in a slum because he cannot imagine what is meant by the offer of a holiday at the sea. We are far too easily pleased.\n\nI do not think that the life of heaven bears any analogy to what is called the soul's union with God. It bears far more analogy to the life we know. We shall eat and drink. There will be work and play and social intercourse. We shall not become disembodied spirits floating in some vast void.\n\nThe weight of glory is this: that the dullest and most uninteresting person you can talk to may one day be a creature which, if you saw it now, you would be strongly tempted to worship, or else a horror and a corruption such as you now meet only in a nightmare. All day long we are, in some degree, helping each other to one or the other of these destinations. It is in the light of these overwhelming possibilities that we should conduct all our dealings with one another.",
        "status": "published",
    },
    {
        "title": "Christ Our Passover",
        "preacher": "Charles H. Spurgeon",
        "date_preached": "1856-04-20",
        "denomination": "Baptist",
        "source_url": "https://www.spurgeon.org/resource-library/sermons/christ-our-passover/",
        "themes": '["Passover", "atonement", "typology", "blood of Christ", "Exodus 12", "Easter"]',
        "summary": "Spurgeon draws rich parallels between the Old Testament Passover lamb and Christ's atoning sacrifice. He examines how every detail of the Passover narrative — the unblemished lamb, the blood on the doorposts, the haste of eating, the bitter herbs — finds its fulfillment in Christ. This typological masterpiece demonstrates Spurgeon's signature Christ-centered hermeneutic.",
        "outline": "I. The Passover lamb — a type of Christ\nII. The slaying of the lamb — the death of Christ\nIII. The blood applied — faith appropriating Christ's sacrifice\nIV. The eating of the lamb — feeding on Christ\nV. The haste and readiness — the pilgrim life",
        "transcript": "Purge out therefore the old leaven, that ye may be a new lump, as ye are unleavened. For even Christ our passover is sacrificed for us (1 Corinthians 5:7). The apostle Paul draws from the ancient ordinance of the Passover a practical lesson for Christian living.\n\nIn Egypt, on that dark and dreadful night when the angel of death passed through the land, each Israelite household was protected by the blood of a lamb. The lamb must be without blemish — a male of the first year. It must be slain, and its blood applied to the doorpost and the lintel. And when the destroying angel saw the blood, he passed over that house.\n\nChrist is our Passover Lamb. He is without blemish and without spot, the Lamb of God who taketh away the sin of the world. He was slain — not accidentally, but deliberately, purposefully, by the determinate counsel and foreknowledge of God. And His blood, when applied by faith to the heart, delivers from the wrath to come.\n\nNote that the lamb must be eaten. It was not enough to slay it, not enough to apply the blood. The household must feed upon the lamb with unleavened bread and bitter herbs. Christ is not merely our protection from judgment — He is our spiritual nourishment. We feed upon Him by faith; we are sustained by His body given for us and His blood shed for us.\n\nAnd observe the haste with which they ate — loins girded, shoes on their feet, staff in hand. They were pilgrims about to march. And so are we. We are strangers and pilgrims on the earth, journeying to a better country. Let us not settle down as though this world were our home, but let us feed on Christ our Passover and press onward to the Promised Land.",
        "status": "published",
    },
    {
        "title": "A Treatise Concerning Religious Affections",
        "preacher": "Jonathan Edwards",
        "date_preached": "1746-01-01",
        "denomination": "Congregational",
        "source_url": "https://www.gutenberg.org/ebooks/34632",
        "themes": '["religious experience", "emotions in worship", "discernment", "true religion", "Great Awakening"]',
        "summary": "Edwards' most systematic theological work, originally delivered as a series of sermons. He addresses the crucial question raised by the Great Awakening: How can genuine religious experience be distinguished from mere emotional excitement? Edwards identifies twelve signs that do not prove affections are gracious and twelve signs that do. This work remains the definitive Christian treatment of religious experience.",
        "outline": "I. The nature of religious affections\nII. Signs that do not indicate true grace\nIII. Signs that do indicate true grace\nIV. The fruit of the Spirit as the ultimate test\nV. Application to the current revival",
        "transcript": "Whom having not seen, ye love; in whom, though now ye see Him not, yet believing, ye rejoice with joy unspeakable and full of glory (1 Peter 1:8). In these words the apostle represents the state of the minds of the Christians to whom he wrote.\n\nThere are true religion and counterfeit religion, and there is no question more important than this: how shall the true be distinguished from the false? In the time of the Great Awakening, there were many who professed great religious experiences. Some of these were genuine, and some were not. And the damage done by those whose experiences proved false was immense, both to themselves and to the cause of religion.\n\nI shall show, first, what are no certain signs that religious affections are truly gracious. Many things which people assume prove their religion genuine do not actually do so. Great intensity of feeling does not prove this. A person may be deeply stirred emotionally and yet not be converted. Tears do not prove it. Much talking about religion does not prove it. Even being zealous for religious duties does not necessarily indicate true grace.\n\nBut secondly, I shall show what signs do attend truly gracious affections. True religious affections arise from divine illumination. They are founded on the moral excellency and beauty of divine things, not on self-interest. They produce a spirit of love, humility, and tenderness. They go together with a conviction of the reality and certainty of divine things. They promote a beautiful symmetry and proportion of the Christian graces, not one virtue alone but all virtues together.\n\nAbove all, the surest sign of true religious affection is found in its fruits — in Christian practice. By their fruits ye shall know them. He that hath my commandments and keepeth them, he it is that loveth me.",
        "status": "published",
    },
    {
        "title": "The Use of the Law",
        "preacher": "John Wesley",
        "date_preached": "1750-01-01",
        "denomination": "Methodist",
        "source_url": "https://www.gutenberg.org/ebooks/author/2632",
        "themes": '["law and gospel", "moral law", "Ten Commandments", "sanctification", "Galatians"]',
        "summary": "Wesley's careful exposition of the relationship between law and gospel. Drawing on Galatians, he identifies three uses of the moral law: to convince sinners of their sin (the pedagogical use), to restrain evil in society (the civil use), and to guide believers in holy living (the normative use). Wesley passionately rejects antinomianism while affirming justification by faith.",
        "outline": "I. The nature and origin of the moral law\nII. The first use — to convince of sin\nIII. The second use — to restrain evil\nIV. The third use — as a guide for believers\nV. The harmony of law and gospel",
        "transcript": "Wherefore the law is holy, and the commandment holy, and just, and good (Romans 7:12). Perhaps there are few subjects within the whole compass of religion so little understood as this. The law of God is the common theme of instruction; yet how seldom is it truly explained!\n\nBy 'the law' I here mean the moral law, contained in the Ten Commandments and enforced by the prophets. The ceremonial law and the Mosaic polity were indeed given by God, but they were intended as temporary provisions for the Jewish nation. The moral law, however, existed from the beginning of the world, being written not on tables of stone but on the hearts of all the children of men when they came out of the hands of their Creator.\n\nThe first use of the law is to convince of sin. It is the looking-glass which shows us our true face. When we hear the law of God — Thou shalt love the Lord thy God with all thy heart, and thy neighbor as thyself — we see how far we have fallen short. The law strips away our self-righteousness and lays bare our true condition before God.\n\nThe second use of the law is to bring us to Christ. The law is our schoolmaster to bring us unto Christ, that we might be justified by faith. It shows us our need and drives us to the Savior. Without the law, we should never know our disease and never seek the remedy.\n\nThe third use of the law is as a guide for the believer. Those who are justified by faith are not freed from the obligation to obey the moral law. On the contrary, they are enabled for the first time to begin truly obeying it. The law tells us what is pleasing to God, and the grace of God enables us to do it. This is the harmony of law and gospel — not contradiction, but completion.",
        "status": "published",
    },
    {
        "title": "Morning and Evening Devotion: The Blood of Jesus",
        "preacher": "Charles H. Spurgeon",
        "date_preached": "1866-03-01",
        "denomination": "Baptist",
        "source_url": "https://www.spurgeon.org/resource-library/sermons/the-blood/",
        "themes": '["blood atonement", "redemption", "cleansing", "1 John 1:7", "assurance"]',
        "summary": "Spurgeon meditates on the power and efficacy of Christ's blood as described in 1 John 1:7 — 'The blood of Jesus Christ His Son cleanseth us from all sin.' He emphasizes both the initial cleansing from guilt and the ongoing purification the blood provides. Spurgeon's devotional warmth combines with theological precision to produce a deeply encouraging message.",
        "outline": "I. The blood that cleanses — whose blood and why it has power\nII. From all sin — the comprehensiveness of the cleansing\nIII. Cleanseth — the present, continuous tense\nIV. Us — the personal application\nV. The assurance this gives the believer",
        "transcript": "The blood of Jesus Christ His Son cleanseth us from all sin (1 John 1:7). Here is the royal remedy for the deepest of all maladies — sin. No other fountain can wash away the foul stain. Natural tears of repentance cannot remove it; works of penance cannot obliterate it; only the blood of Jesus can deal with it.\n\nNote that the apostle says 'the blood' — not the example, not the teaching, not the influence of Jesus, though all these are precious. It is His blood — His sacrificial death — which is the ground of our cleansing. Without shedding of blood there is no remission. The blood was the price paid; the blood is the fountain opened.\n\nAnd mark the present tense: 'cleanseth.' Not 'will cleanse at some future day,' nor 'did cleanse at some past moment,' but cleanseth — continually, perpetually, in an ongoing flow of purifying power. The blood of Christ is as fresh today as when it flowed on Calvary. Its efficacy is not diminished by time. Every moment we need it, and every moment it is available.\n\n'From all sin.' Not from some sins, not from little sins, not from past sins only, but from ALL sin. The blood of Christ is able to cleanse the greatest sinner as well as the least. It can deal with sins of youth and sins of age, sins known and sins unknown, sins of thought and sins of deed.\n\nAnd observe for whom this cleansing is available: 'us.' Not merely for the apostles, not only for the first Christians, but for all believers in every age. If you trust in Christ, this promise is for you. The blood of Jesus Christ His Son cleanseth us — you and me — from all sin. What comfort! What assurance! What reason for praise!",
        "status": "published",
    },
    {
        "title": "On the Death of Rev. George Whitefield",
        "preacher": "John Wesley",
        "date_preached": "1770-11-18",
        "denomination": "Methodist",
        "source_url": "https://www.gutenberg.org/ebooks/author/2632",
        "themes": '["eulogy", "friendship", "legacy", "evangelism", "George Whitefield", "ministry"]',
        "summary": "Wesley's moving funeral sermon for his longtime friend and sometime theological rival George Whitefield, who died on September 30, 1770. Despite their well-known differences (Wesley was Arminian, Whitefield Calvinist), Wesley pays generous tribute to Whitefield's extraordinary gifts, tireless labor, and Christ-like character. The sermon is a model of Christian charity and honest remembrance.",
        "outline": "I. George Whitefield's conversion and early ministry\nII. His extraordinary preaching gifts\nIII. His tireless evangelistic labors across two continents\nIV. His personal character and piety\nV. Lessons from his life and death",
        "transcript": "Let me die the death of the righteous, and let my last end be like his (Numbers 23:10). We are here met together to perform the last sad office of Christian love to one who, we trust, is now entered into the joy of his Lord.\n\nGeorge Whitefield was born in Gloucester on the sixteenth of December, 1714. Even in his youth there were tokens of what God intended to do by him. He was early impressed with religious concern, and while a student at Oxford, became acquainted with the Wesleys and the little 'Holy Club,' as it was then derisively called. But it was not until some time after that he came to a clear understanding of salvation by faith alone.\n\nHis gifts as a preacher were unparalleled in his generation. I may safely affirm that no minister in our age has been so generally useful as he. He preached to immense congregations — sometimes twenty, sometimes thirty, sometimes forty thousand hearers. And his voice was so powerful that every person could hear him distinctly. But it was not merely loudness; it was a clarity, a pathos, an earnestness that pierced the heart.\n\nHe labored more abundantly than any other man of his generation. In the compass of a single week, he would often preach ten or twelve times, besides attending to private counsel and correspondence. He crossed the Atlantic thirteen times, preaching in virtually every major town in England, Scotland, Wales, and the American colonies. His body was the temple of toil, and he spared it not.\n\nWhat shall we say of his character? He was of a generous and charitable disposition. He was remarkably cheerful and of a forgiving spirit. Though he and I differed on certain points of doctrine — and these differences were well known — yet I can testify that I knew him intimately for more than thirty years, and never once heard him speak an unkind word of any person.\n\nLet us then, my brethren, take the lessons of his life to heart. Have we his burning zeal for souls? Have we his willingness to endure hardship for the gospel? Let us follow his example, as he followed Christ's, and let us pray that God would raise up many more such laborers in His harvest.",
        "status": "published",
    },
    {
        "title": "The Duty of a Christian to Make Progress",
        "preacher": "Martin Luther",
        "date_preached": "1518-01-01",
        "denomination": "Lutheran",
        "source_url": "https://www.gutenberg.org/ebooks/author/65",
        "themes": '["sanctification", "growth", "Reformation", "faith and works", "Christian life"]',
        "summary": "Luther challenges Christians not to rest on the initial experience of conversion but to press forward in faith and holiness. He uses Paul's example of pressing toward the mark (Philippians 3:14) to argue that the Christian life is a dynamic journey, not a static state. Luther warns against spiritual complacency while maintaining that all growth is empowered by grace.",
        "outline": "I. The danger of spiritual complacency\nII. Paul's example — pressing toward the mark\nIII. What Christian progress looks like\nIV. The means of growth — Word and Sacrament\nV. Encouragement to persevere",
        "transcript": "Brethren, I count not myself to have apprehended; but this one thing I do, forgetting those things which are behind, and reaching forth unto those things which are before (Philippians 3:13). We must not think that we have arrived. We must not rest. The Christian life is a race that is not won at the starting line but at the finish.\n\nThe great apostle Paul, who had labored more abundantly than all the rest, who had been caught up to the third heaven and heard unspeakable words, who had planted churches across the known world — this same apostle says, 'I count not myself to have apprehended.' If Paul had not arrived, what shall we say of ourselves? Let every man examine himself and ask: Am I going forward, or am I standing still?\n\nThere are Christians who received the grace of God ten years ago and are no further along today than they were then. They know the same truths, they pray the same prayers, they commit the same sins. They have rested on the grace they received and have not pressed on to deeper knowledge, greater holiness, and more fervent love. These are trees that bear leaves but no fruit.\n\nBut what does it mean to make progress? It means to grow in faith — to believe more firmly, more constantly, more joyfully. It means to grow in love — to love God more ardently and our neighbor more truly. It means to grow in hope — to look forward with greater certainty to the consummation of all things.\n\nThe means of this progress are not mysterious. God has given us His Word, which is a lamp to our feet. He has given us the sacraments, which are visible signs of invisible grace. He has given us prayer, which is the breathing of the soul. He has given us the fellowship of believers, in which iron sharpens iron.\n\nTherefore, dear brethren, let us not be content with yesterday's faith. Let us press on toward the mark of the high calling of God in Christ Jesus. The race is before us, the prize is above us, and the grace of God is sufficient for us.",
        "status": "published",
    },
    {
        "title": "Concerning Christian Liberty",
        "preacher": "Martin Luther",
        "date_preached": "1520-01-01",
        "denomination": "Lutheran",
        "source_url": "https://www.gutenberg.org/ebooks/1911",
        "themes": '["Christian liberty", "Reformation", "faith alone", "priesthood of believers", "two kingdoms"]',
        "summary": "One of Luther's three great Reformation treatises. He presents the paradox at the heart of Christian existence: 'A Christian is a perfectly free lord of all, subject to none. A Christian is a perfectly dutiful servant of all, subject to all.' Luther explains how faith in Christ frees us from the law's condemnation while love compels us to serve our neighbor. This work shaped the entire trajectory of Protestant theology.",
        "outline": "I. The twofold nature of Christian existence\nII. Faith alone justifies — the inner freedom\nIII. Love serves the neighbor — the outward expression\nIV. Works as fruits of faith, not means of salvation\nV. The priesthood of all believers",
        "transcript": "A Christian is a perfectly free lord of all, subject to none. A Christian is a perfectly dutiful servant of all, subject to all. These two theses seem to contradict each other. If, however, they should be found to fit together they would serve our purpose beautifully.\n\nFirst, let us consider the inner man. The soul can do without everything except the Word of God, and apart from the Word of God nothing can help the soul. But having the Word, the soul needs nothing else. In the Word it has food, joy, peace, light, understanding, justice, truth, wisdom, liberty, and every good thing in abundance. Thus it is clear that a Christian has all that he needs in faith and needs no works to justify him.\n\nBut does this mean that he should be idle and do no good works? By no means! Here we come to the second proposition. While the inner man is perfectly free through faith, the outer man must be the servant of all. Although we are free from all works as far as justification is concerned, yet in this mortal life on earth we dwell in our bodies and among other human beings. Here works begin; here the body must not be idle.\n\nFor faith, as it produces love, must pour itself out in service. Just as our heavenly Father has freely helped us through Christ, so we ought freely to help our neighbor through our body and its works. Each should become as it were a Christ to the other, that we may be truly Christians.\n\nWho then can comprehend the riches and the glory of the Christian life? It can do all things and has all things and lacks nothing. It is lord over sin, death, and hell, and yet is the most dutiful servant, employed in the service of all. This is the liberty wherewith Christ has made us free — not a liberty for the flesh, but a liberty that serves in love.",
        "status": "published",
    },
    {
        "title": "Charity and Its Fruits",
        "preacher": "Jonathan Edwards",
        "date_preached": "1738-01-01",
        "denomination": "Congregational",
        "source_url": "https://www.gutenberg.org/ebooks/34632",
        "themes": '["love", "1 Corinthians 13", "virtue", "Christian ethics", "heaven"]',
        "summary": "Edwards' beautiful sermon series on 1 Corinthians 13, expounding each attribute of love. He argues that love (charity) is the very essence of true religion and that all other graces and gifts are worthless without it. The series culminates with a stunning vision of heaven as the 'world of love' where charity reaches its perfection.",
        "outline": "I. Love as the sum of all virtue\nII. Love suffers long — patience\nIII. Love is kind — active benevolence\nIV. Love envieth not — contentment in others' good\nV. Heaven — the world of love",
        "transcript": "Though I speak with the tongues of men and of angels, and have not charity, I am become as sounding brass, or a tinkling cymbal (1 Corinthians 13:1). The apostle, in the foregoing chapter, had been speaking of the extraordinary gifts of the Spirit.\n\nHe had enumerated the gift of prophecy, the gift of tongues, the gift of healing, and the other wonderful endowments by which God adorned the early church. But now, having displayed all these glittering gifts, he says in effect: 'I show unto you a more excellent way.' That way is charity — love — without which all other gifts are empty noise.\n\nConsider what the apostle declares. A man may have the tongue of an angel — the most eloquent, the most sublime, the most moving speech that ever fell on human ears — and yet if love is absent, it is all nothing. Brass makes a great sound, but there is no music in it. A cymbal crashes and clangs, but it neither comforts nor instructs. So is the man of great gifts but no love.\n\nSo also with knowledge. 'Though I understand all mysteries, and all knowledge.' A man may penetrate the deepest truths of theology, may unravel the most difficult passages of Scripture, may stand at the summit of intellectual achievement — and yet without love, he is nothing. Knowledge puffeth up, but charity buildeth up.\n\nAnd what is this charity? Charity suffereth long, and is kind. It beareth all things, believeth all things, hopeth all things, endureth all things. It is not a mere sentiment or emotion. It is a settled disposition of the heart toward God and toward our fellow creatures, wrought in us by the Holy Spirit. It is the very essence of the divine nature communicated to the human soul.\n\nHeaven itself is nothing other than a world of love. There charity shall be perfected. There the saints shall love God with a love unmixed with selfishness, and one another with a love undimmed by envy. Let us, then, covet earnestly the best gift — which is love.",
        "status": "published",
    },
    {
        "title": "The Expulsive Power of a New Affection",
        "preacher": "Thomas Chalmers",
        "date_preached": "1817-01-01",
        "denomination": "Presbyterian",
        "source_url": "https://www.gutenberg.org/ebooks/author/1765",
        "themes": '["desire", "love of God", "sanctification", "worldliness", "heart transformation"]',
        "summary": "Chalmers' most famous sermon argues that the only way to overcome love for the world is not by proving its vanity, but by establishing a superior affection — love for God through Christ. He demonstrates that mere intellectual conviction of the world's emptiness cannot change the heart; only a new and greater love can displace the old. This psychological and spiritual masterpiece influenced generations of preachers.",
        "outline": "I. The futility of merely exposing the world's emptiness\nII. The heart cannot be left in a vacuum\nIII. A new affection must displace the old\nIV. The love of God as the expulsive power\nV. How the gospel creates this new affection",
        "transcript": "Love not the world, neither the things that are in the world. If any man love the world, the love of the Father is not in him (1 John 2:15). There are two ways in which a practical moralist may attempt to displace from the human heart its love of the world.\n\nThe first way is to demonstrate the world's vanity — to show that its pleasures are fleeting, its riches uncertain, its honors empty. This is the method of the preacher of Ecclesiastes: Vanity of vanities, all is vanity. It is true, of course. Every word of it is true. And yet this method, by itself, seldom succeeds. The heart that is emptied of one love, but not filled with another, will simply return to the old affection as soon as the impression fades.\n\nThe second way — and the only effectual way — is to set forth the superior excellence of a new object of affection. You cannot destroy the love of the world merely by exposing its worthlessness. But you can supplant it by awakening a love for something infinitely better. This is the expulsive power of a new affection.\n\nConsider how this works in common life. The child outgrows the toy not because someone proved its worthlessness, but because a new interest — a book, a companion, a pursuit — captured his heart. The young man abandons frivolous amusements not because a lecture convinced him, but because a great purpose seized his soul.\n\nSo it is in the spiritual life. The love of God, shed abroad in the heart by the Holy Ghost, is the only power sufficient to dislodge the love of the world. When the glory of Christ is revealed to the soul — His beauty, His grace, His sacrificial love — then the trinkets of the world lose their hold. Not because they are argued away, but because they are outshone.\n\nThis is why the gospel is the true instrument of moral transformation. It does not merely command us to stop loving the world. It presents to us One who is fairer than the children of men, One in whose presence earthly pleasures grow dim. The new affection does not leave the heart vacant; it fills it to overflowing with a joy that the world can neither give nor take away.",
        "status": "published",
    },
]

# ─── Scripture references for sermons ────────────────────────────────────────

SCRIPTURES = [
    {"book": "Deuteronomy", "chapter": 32, "verse_start": 35, "verse_end": 35, "text": "Their foot shall slide in due time.", "translation": "KJV"},
    {"book": "John", "chapter": 3, "verse_start": 7, "verse_end": 7, "text": "Marvel not that I said unto thee, Ye must be born again.", "translation": "KJV"},
    {"book": "Malachi", "chapter": 3, "verse_start": 6, "verse_end": 6, "text": "For I am the LORD, I change not; therefore ye sons of Jacob are not consumed.", "translation": "KJV"},
    {"book": "Romans", "chapter": 8, "verse_start": 32, "verse_end": 32, "text": "He that spared not his own Son, but delivered him up for us all, how shall he not with him also freely give us all things?", "translation": "KJV"},
    {"book": "Matthew", "chapter": 16, "verse_start": 17, "verse_end": 17, "text": "Blessed art thou, Simon Bar-Jonah: for flesh and blood hath not revealed it unto thee, but my Father which is in heaven.", "translation": "KJV"},
    {"book": "Acts", "chapter": 26, "verse_start": 28, "verse_end": 28, "text": "Almost thou persuadest me to be a Christian.", "translation": "KJV"},
    {"book": "Romans", "chapter": 4, "verse_start": 5, "verse_end": 5, "text": "But to him that worketh not, but believeth on him that justifieth the ungodly, his faith is counted for righteousness.", "translation": "KJV"},
    {"book": "Luke", "chapter": 14, "verse_start": 23, "verse_end": 23, "text": "Go out into the highways and hedges, and compel them to come in, that my house may be filled.", "translation": "KJV"},
    {"book": "1 Corinthians", "chapter": 5, "verse_start": 7, "verse_end": 7, "text": "For even Christ our passover is sacrificed for us.", "translation": "KJV"},
    {"book": "1 Peter", "chapter": 1, "verse_start": 8, "verse_end": 8, "text": "Whom having not seen, ye love; in whom, though now ye see him not, yet believing, ye rejoice with joy unspeakable and full of glory.", "translation": "KJV"},
    {"book": "1 John", "chapter": 1, "verse_start": 7, "verse_end": 7, "text": "The blood of Jesus Christ his Son cleanseth us from all sin.", "translation": "KJV"},
    {"book": "Philippians", "chapter": 3, "verse_start": 13, "verse_end": 14, "text": "Brethren, I count not myself to have apprehended: but this one thing I do, forgetting those things which are behind, and reaching forth unto those things which are before, I press toward the mark.", "translation": "KJV"},
    {"book": "1 Corinthians", "chapter": 13, "verse_start": 1, "verse_end": 13, "text": "Though I speak with the tongues of men and of angels, and have not charity, I am become as sounding brass, or a tinkling cymbal.", "translation": "KJV"},
    {"book": "1 John", "chapter": 2, "verse_start": 15, "verse_end": 15, "text": "Love not the world, neither the things that are in the world.", "translation": "KJV"},
]

# Mapping: sermon title → scripture indices (0-based into SCRIPTURES list)
SERMON_SCRIPTURE_MAP = {
    "Sinners in the Hands of an Angry God": [0],
    "The New Birth": [1],
    "The Immutability of God": [2],
    "The Free Grace of God": [3],
    "A Divine and Supernatural Light": [4],
    "The Almost Christian": [5],
    "Justification by Faith": [6],
    "Compel Them to Come In": [7],
    "Christ Our Passover": [8],
    "A Treatise Concerning Religious Affections": [9],
    "Morning and Evening Devotion: The Blood of Jesus": [10],
    "The Duty of a Christian to Make Progress": [11],
    "Charity and Its Fruits": [12],
    "The Expulsive Power of a New Affection": [13],
}


async def seed():
    engine = get_engine()

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = get_session_factory()
    async with factory() as session:
        # Check if sermons already exist
        from sqlalchemy import select, func
        count_result = await session.execute(select(func.count(Sermon.id)))
        existing = count_result.scalar() or 0
        if existing > 0:
            print(f"Database already has {existing} sermons. Skipping seed.")
            return

        # Insert scriptures
        scripture_objs = []
        for s in SCRIPTURES:
            obj = Scripture(**s)
            session.add(obj)
            scripture_objs.append(obj)
        await session.flush()  # Get IDs assigned

        # Insert sermons
        sermon_objs = []
        for s_data in SERMONS:
            sermon = Sermon(**s_data)
            session.add(sermon)
            sermon_objs.append(sermon)
        await session.flush()

        # Create sermon-scripture links
        for sermon in sermon_objs:
            scripture_indices = SERMON_SCRIPTURE_MAP.get(sermon.title, [])
            for idx in scripture_indices:
                link = SermonScripture(
                    sermon_id=sermon.id,
                    scripture_id=scripture_objs[idx].id,
                    context=f"Primary text for '{sermon.title}'"
                )
                session.add(link)

        await session.commit()
        print(f"✓ Seeded {len(sermon_objs)} sermons, {len(scripture_objs)} scriptures")


if __name__ == "__main__":
    asyncio.run(seed())
