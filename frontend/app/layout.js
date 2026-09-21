import "./globals.css";

export const metadata = {
  title: "ProPopuli",
  description: "High-integrity, friction-enforced discussion",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
