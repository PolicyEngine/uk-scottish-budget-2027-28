// Compact PolicyEngine site footer, as on the Autumn Budget 2026 dashboard:
// small white logo, the links in one row, copyright. Replaces the ui-kit
// shell's own footer (PolicyEngineShell showFooter={false}).
import { basePath as BASE_PATH } from "../lib/basePath.json";

const FOOTER_LINKS = [
  { label: "About us", href: "https://policyengine.org/uk/team" },
  { label: "Donate", href: "https://policyengine.org/uk/donate" },
  { label: "Developer tools", href: "https://policyengine.org/uk/dev-tools" },
  { label: "Privacy policy", href: "https://policyengine.org/uk/privacy" },
  { label: "Terms and conditions", href: "https://policyengine.org/uk/terms" },
];

export default function SiteFooter() {
  return (
    <footer className="site-footer">
      <div className="site-footer-inner">
        <a href="https://policyengine.org/uk" aria-label="PolicyEngine UK home" className="site-footer-logo">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={`${BASE_PATH}/assets/logos/policyengine-white.svg`} alt="PolicyEngine" />
        </a>
        <nav aria-label="PolicyEngine site footer" className="site-footer-links">
          {FOOTER_LINKS.map((link) => (
            <a key={link.label} href={link.href}>
              {link.label}
            </a>
          ))}
        </nav>
        <p className="site-footer-copy">&copy; {new Date().getFullYear()} PolicyEngine</p>
      </div>
    </footer>
  );
}
