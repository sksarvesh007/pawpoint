"use client";

import { useState } from "react";

interface FAQItem {
  question: string;
  answer: string;
}

const faqData: FAQItem[] = [
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

export function FAQAccordion() {
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  const toggleQuestion = (index: number) => {
    setOpenIndex(openIndex === index ? null : index);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-4">
      {faqData.map((faq, index) => (
        <div
          key={index}
          className="bg-white rounded-2xl border-2 border-gray-100 overflow-hidden hover:border-[#3DA99F]/30 transition-all duration-300"
        >
          <button
            onClick={() => toggleQuestion(index)}
            className="w-full px-8 py-6 flex items-center justify-between text-left hover:bg-gray-50/50 transition-colors"
          >
            <h3 className="text-[18px] font-nunito font-bold text-[#1D3533] pr-4">
              {faq.question}
            </h3>
            <div
              className={`flex-shrink-0 w-8 h-8 rounded-full bg-[#3DA99F]/10 flex items-center justify-center transition-transform duration-300 ${
                openIndex === index ? "rotate-180" : ""
              }`}
            >
              <svg
                width="16"
                height="16"
                viewBox="0 0 16 16"
                fill="none"
                className="text-[#3DA99F]"
              >
                <path
                  d="M4 6L8 10L12 6"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            </div>
          </button>
          <div
            className={`transition-all duration-300 ease-in-out ${
              openIndex === index
                ? "max-h-[500px] opacity-100"
                : "max-h-0 opacity-0"
            } overflow-hidden`}
          >
            <div className="px-8 pb-6 pt-2">
              <p className="text-[16px] text-[#5C6F6C] leading-relaxed font-medium">
                {faq.answer}
              </p>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
