import { CheckCircle2 } from "lucide-react";

const steps = [
  "HELLO",
  "KYBER_PUBLIC_KEY",
  "KYBER_CIPHERTEXT",
  "KEY_CONFIRM",
  "DATA",
  "REHANDSHAKE",
];

export default function HandshakeTimeline({
  current = "DATA",
}) {

  const activeIndex = steps.indexOf(current);

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">

      <h2 className="mb-8 text-xl font-semibold text-white">
        Protocol Handshake
      </h2>

      <div className="space-y-6">

        {steps.map((step, index) => {

          const active = index <= activeIndex;

          return (

            <div
              key={step}
              className="flex items-center gap-4"
            >

              <div
                className={`flex h-10 w-10 items-center justify-center rounded-full border transition-all
                ${
                  active
                    ? "border-green-500 bg-green-500/20"
                    : "border-slate-700 bg-slate-800"
                }`}
              >

                <CheckCircle2
                  size={18}
                  className={
                    active
                      ? "text-green-400"
                      : "text-slate-600"
                  }
                />

              </div>

              <div className="flex-1">

                <p
                  className={`font-medium ${
                    active
                      ? "text-white"
                      : "text-slate-500"
                  }`}
                >
                  {step}
                </p>

              </div>

            </div>

          );

        })}

      </div>

    </div>
  );
}