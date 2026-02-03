import { Metadata } from "next";
import { redirect, notFound } from "next/navigation";
import { getClinicPublicInfo } from "@/lib/api/chat";

interface PageProps {
  params: Promise<{ slug: string }>;
}

/**
 * Generate metadata for the clinic page
 */
export async function generateMetadata({
  params,
}: PageProps): Promise<Metadata> {
  const { slug } = await params;

  try {
    const clinicInfo = await getClinicPublicInfo(slug);
    return {
      title: `${clinicInfo.clinic_name} | PawPoint`,
      description: `Welcome to ${clinicInfo.clinic_name}`,
    };
  } catch {
    return {
      title: "Clinic Not Found | PawPoint",
    };
  }
}

/**
 * Clinic landing page - redirects to chat
 * Accessible at /{clinic-slug}
 */
export default async function ClinicPage({ params }: PageProps) {
  const { slug } = await params;

  // Verify clinic exists
  try {
    await getClinicPublicInfo(slug);
  } catch {
    notFound();
  }

  // Redirect to chat page
  redirect(`/${slug}/chat`);
}
