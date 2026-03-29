import { HeroSection } from "@/components/hero-section";
import { Navbar } from "@/components/navbar";
import { FeaturesSection } from "@/components/features-section";

export default function Home() {
  return (
    <>
      <Navbar />
      <main className="flex-1">
        <HeroSection />
        <FeaturesSection />
      </main>
      <footer className="border-t border-border py-8 text-center text-muted-foreground text-sm">
        <p>&copy; {new Date().getFullYear()} Apologia. All rights reserved.</p>
      </footer>
    </>
  );
}
