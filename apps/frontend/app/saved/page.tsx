import { SavedCompaniesList } from "@/components/search/saved-companies-list";

export default function SavedPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Saved Companies</h1>
        <p className="text-muted-foreground">
          Track your target companies and monitor sponsorship activity over time.
        </p>
      </div>
      <SavedCompaniesList />
    </div>
  );
}
