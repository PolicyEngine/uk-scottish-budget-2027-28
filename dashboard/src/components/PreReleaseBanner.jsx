// The banner on every view. A drill build (NEXT_PUBLIC_MOCK set at build
// time) says MOCK first, as every drill rubric checks; otherwise it is the
// pre-release notice. It is the page's one statement of either.
export const PRE_RELEASE_TEXT =
  "Pre-release template — placeholder figures. Not a costing of the Scottish Budget 2027-28.";
export const MOCK_TEXT =
  "MOCK — drill figures from a mock statement, not the Scottish Budget 2027-28. Not for publication.";

export function bannerText(mock = process.env.NEXT_PUBLIC_MOCK) {
  return mock && mock !== "0" ? MOCK_TEXT : PRE_RELEASE_TEXT;
}

export default function PreReleaseBanner() {
  return (
    <div className="pre-release-banner" role="status" data-testid="pre-release-banner">
      {bannerText()}
    </div>
  );
}
