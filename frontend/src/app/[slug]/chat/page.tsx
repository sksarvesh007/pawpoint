import { Metadata } from "next";
import { notFound } from "next/navigation";
import ClientChatPage from "./ClientChatPage";
import { getClinicPublicInfo } from "@/lib/api/chat";

interface PageProps {
  params: Promise<{ slug: string }>;
}

/**
 * Generate metadata for the chat page
 */
export async function generateMetadata({
  params,
}: PageProps): Promise<Metadata> {
  const { slug } = await params;

  try {
    const clinicInfo = await getClinicPublicInfo(slug);
    return {
      title: `Chat with ${clinicInfo.clinic_name} | PawPoint`,
      description: `Chat with the AI assistant at ${clinicInfo.clinic_name}`,
    };
  } catch {
    return {
      title: "Clinic Not Found | PawPoint",
    };
  }
}

/**
 * Public chatbot page for each clinic
 * Accessible at /{clinic-slug}/chat
 */
export default async function ChatPage({ params }: PageProps) {
  const { slug } = await params;

  // Fetch clinic info server-side
  let clinicInfo;
  try {
    clinicInfo = await getClinicPublicInfo(slug);
  } catch {
    // If clinic not found, show 404
    notFound();
  }

  return <ClientChatPage slug={slug} clinicInfo={clinicInfo} />;
}
