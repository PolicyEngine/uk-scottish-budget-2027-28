import { PolicyEngineShell } from "@policyengine/ui-kit/layout";
import "@policyengine/ui-kit/styles.css";
import localFont from "next/font/local";
import PreReleaseBanner from "../src/components/PreReleaseBanner";
import SiteFooter from "../src/components/SiteFooter";
import { SITE_HEADER_STYLES, SITE_NAV_ITEMS } from "../src/utils/siteNav";

import "./globals.css";
// The PolicyEngine tokens (--pe-color-* and the rest), bundled with the
// page, as on the Autumn Budget 2026 dashboard.
import "@policyengine/ui-kit/legacy/tokens.css";
import "./fonts.css";
import "./siteHeader.css";

// Inter, committed with the page (fonts/: the variable face, Latin subset;
// SIL Open Font License in fonts/OFL.txt), so no font is fetched from a
// third party.
const inter = localFont({
  src: "./fonts/inter-latin-variable.woff2",
  weight: "100 900",
  style: "normal",
  display: "swap",
  variable: "--font-inter",
  adjustFontFallback: "Arial",
});

export const metadata = {
  title: "Scottish Budget 2027-28 (pre-release template) | PolicyEngine",
  description:
    "Pre-release template of the PolicyEngine dashboard for the Scottish Budget 2027-28. All figures are placeholders.",
  // Pre-release template: never indexed. Remove only at G4 on the real day,
  // with the canonical address, title, description and social card.
  robots: { index: false, follow: false, nocache: true },
};

export const viewport = { width: "device-width", initialScale: 1 };

export default function RootLayout({ children }) {
  return (
    <html lang="en-GB" className={inter.variable}>
      <body>
        <PreReleaseBanner />
        <PolicyEngineShell
          country="uk"
          showFooter={false}
          headerProps={{ navItems: SITE_NAV_ITEMS, styles: SITE_HEADER_STYLES }}
        >
          {children}
          <SiteFooter />
        </PolicyEngineShell>
      </body>
    </html>
  );
}
