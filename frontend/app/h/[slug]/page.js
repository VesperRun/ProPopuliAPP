import { redirect } from "next/navigation";

export default function LegacyHubRedirect({ params }) {
  redirect(`/s/${params.slug}`);
}
