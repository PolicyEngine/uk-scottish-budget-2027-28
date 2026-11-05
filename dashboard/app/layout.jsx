import PolicyEngineFooter from "../src/components/PolicyEngineFooter";
import PolicyEngineHeader from "../src/components/PolicyEngineHeader";
import PreReleaseBanner from "../src/components/PreReleaseBanner";

import "./globals.css";

export const metadata = {
  title: "Scottish Budget 2027-28 (pre-release template) | PolicyEngine",
  description:
    "Pre-release template of the PolicyEngine dashboard for the Scottish Budget 2027-28. All figures are placeholders.",
  // Pre-release template: never indexed. Remove only at G4 on the real day.
  robots: { index: false, follow: false, nocache: true },
};

export default function RootLayout({ children }) {
  return (
    <html lang="en-GB">
      <body>
        <PreReleaseBanner />
        <PolicyEngineHeader />
        {children}
        <PolicyEngineFooter />
      </body>
    </html>
  );
}
