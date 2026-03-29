import { Navbar } from "@/components/navbar";
import { SermonsPage } from "./sermons-page";

export default function Sermons() {
  return (
    <>
      <Navbar />
      <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <div className="mb-8">
          <h1 className="text-3xl font-bold">Sermons</h1>
        </div>
        <SermonsPage />
      </main>
    </>
  );
}
