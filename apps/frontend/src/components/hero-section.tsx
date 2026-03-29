export function HeroSection() {
  return (
    <section className="relative py-24 px-4 sm:px-6 lg:px-8 overflow-hidden">
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-primary/10" />
      
      <div className="relative max-w-4xl mx-auto text-center">
        <h1 className="text-5xl sm:text-6xl font-bold tracking-tight text-foreground mb-6">
          The World&apos;s Sermons,{" "}
          <span className="text-primary">Connected by AI</span>
        </h1>
        <p className="text-xl text-muted-foreground max-w-2xl mx-auto mb-10">
          Explore thousands of sermons, discover thematic connections, and prepare
          your own messages with AI-powered tools built for pastors and preachers.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <a
            href="/sermons"
            className="bg-primary text-primary-foreground px-8 py-3 rounded-lg text-lg font-medium hover:bg-primary/90 transition-colors"
          >
            Explore Sermons
          </a>
          <a
            href="/workbench"
            className="border border-border text-foreground px-8 py-3 rounded-lg text-lg font-medium hover:bg-secondary transition-colors"
          >
            Open Workbench
          </a>
        </div>
      </div>
    </section>
  );
}
