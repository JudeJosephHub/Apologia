const features = [
  {
    icon: "🔍",
    title: "Semantic Search",
    description:
      "Find sermons by meaning, not just keywords. Our AI understands theology and context.",
  },
  {
    icon: "🕸️",
    title: "Sermon Graph",
    description:
      "Visualize connections between sermons — thematic, scriptural, and topical links rendered as an interactive graph.",
  },
  {
    icon: "✍️",
    title: "Pastor Workbench",
    description:
      "Draft, brainstorm, and refine your sermons with AI-powered writing assistance.",
  },
  {
    icon: "📚",
    title: "Scripture Cross-Reference",
    description:
      "Every sermon mapped to its scripture references. Find all sermons on any passage.",
  },
  {
    icon: "🎓",
    title: "Structured Courses",
    description:
      "Organize sermons into curated learning paths for Bible study groups and seminary training.",
  },
  {
    icon: "🎙️",
    title: "Audio Transcription",
    description:
      "Upload sermon audio and get AI-powered transcripts, summaries, and automatic tagging.",
  },
];

export function FeaturesSection() {
  return (
    <section className="py-20 px-4 sm:px-6 lg:px-8 bg-card">
      <div className="max-w-6xl mx-auto">
        <h2 className="text-3xl font-bold text-center mb-4">
          Everything You Need for Sermon Ministry
        </h2>
        <p className="text-muted-foreground text-center max-w-2xl mx-auto mb-16">
          From research to delivery, Apologia equips pastors with AI-enhanced
          tools rooted in biblical scholarship.
        </p>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature) => (
            <div
              key={feature.title}
              className="p-6 rounded-xl border border-border bg-background hover:shadow-lg transition-shadow"
            >
              <span className="text-3xl mb-4 block">{feature.icon}</span>
              <h3 className="font-semibold text-lg mb-2">{feature.title}</h3>
              <p className="text-muted-foreground text-sm">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
