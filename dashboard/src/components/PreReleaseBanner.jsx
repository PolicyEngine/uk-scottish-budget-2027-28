export const BANNER_TEXT = "Pre-release template — placeholder figures. Not a costing of the Scottish Budget 2027-28.";

export default function PreReleaseBanner() {
  return (
    <div className="pre-release-banner" role="status" data-testid="pre-release-banner">
      {BANNER_TEXT}
    </div>
  );
}
