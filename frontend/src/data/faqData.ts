export interface FAQItem {
  question: string;
  answer: string;
}

export const faqData: FAQItem[] = [
  {
    question: "What exactly does PawPoint do?",
    answer:
      "PawPoint is an AI receptionist that answers calls, collects client and pet information, and captures appointment requests. It ensures no calls are missed, messages are organized, and urgent issues are flagged — helping your team focus on caring for pets while maximizing bookings and revenue.",
  },
  {
    question: "Does PawPoint integrate directly with my clinic's PIMS?",
    answer:
      "PawPoint works with or without PIMS integration. Initially, it captures appointment requests and notifies your staff via email or your hospital's dashboard. For clinics with accessible PIMS systems, PawPoint can later integrate directly to streamline appointment scheduling.",
  },
  {
    question: "How does PawPoint handle new vs existing clients?",
    answer:
      "The AI can distinguish between new and returning clients, asking for pet details, appointment type, and preferred time. This information is clearly organized in the staff dashboard so you can prioritize urgent requests and quickly confirm appointments.",
  },
  {
    question: "Can PawPoint handle after-hours calls?",
    answer:
      "Yes! PawPoint is available 24/7, including nights, weekends, and holidays. It can take messages, collect intake information, and flag urgent cases for immediate staff attention or follow-up, ensuring your clinic never misses an opportunity to care for pets.",
  },
  {
    question: "Will PawPoint sound robotic to my clients?",
    answer:
      "Not at all! PawPoint uses natural, conversational speech designed to be friendly, professional, and reassuring. Clients will feel like they're talking to a helpful receptionist, not a machine.",
  },
  {
    question: "How will my staff know about new appointment requests?",
    answer:
      "All incoming requests are sent in real time to your staff via your preferred method (dashboard notifications, email summaries, etc.). Staff can quickly review, confirm, and schedule the appointment without missing a beat. For those clinics using PIMS integrations, the appointments will automatically be added to your schedule – with no staff having to handle it.",
  },
  {
    question: "How can PawPoint help my clinic grow revenue?",
    answer:
      "Studies show that 1 in 4 calls to vet clinics is missed, often resulting in lost appointments and clients. PawPoint ensures every call is captured, every appointment request is logged, and urgent cases are prioritized. By reducing missed calls, improving client experience, and increasing booking efficiency, clinics see more appointments, repeat visits, and measurable revenue growth.",
  },
  {
    question: "How long does it take to integrate PawPoint with my clinic?",
    answer:
      "PawPoint is designed for fast, hassle-free setup. Most clinics are fully up and running within 24–48 hours, with no PIMS integration required. For clinics that want PIMS integration in the future, the timeline may vary depending on the system, but initial call handling and appointment capture can start immediately, ensuring your clinic never misses another call.",
  },
];
