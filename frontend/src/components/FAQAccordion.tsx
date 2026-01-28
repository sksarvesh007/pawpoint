"use client";

import { useState } from "react";
import { faqData } from "@/data/faqData";

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
