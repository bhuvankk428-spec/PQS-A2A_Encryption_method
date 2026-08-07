import {
  Lock,
  Unlock,
  ArrowDown,
} from "lucide-react";

export default function EncryptionViewer({
  plaintext = "",
  ciphertext = "",
  decrypted = "",
}) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">

      <h2 className="mb-8 text-xl font-semibold text-white">
        Encryption Pipeline
      </h2>

      <div className="space-y-5">

        {/* Plaintext */}

        <Block
          title="Plaintext"
          value={plaintext}
          color="text-green-400"
        />

        <Arrow />

        {/* Encrypt */}

        <MiddleBlock
          icon={<Lock size={22} />}
          title="AES-256-GCM Encrypt"
        />

        <Arrow />

        {/* Cipher */}

        <Block
          title="Ciphertext"
          value={ciphertext}
          color="text-cyan-400"
          mono
        />

        <Arrow />

        {/* Decrypt */}

        <MiddleBlock
          icon={<Unlock size={22} />}
          title="AES-256-GCM Decrypt"
        />

        <Arrow />

        {/* Result */}

        <Block
          title="Recovered Plaintext"
          value={decrypted}
          color="text-green-400"
        />

      </div>

    </div>
  );
}

function Arrow() {
  return (
    <div className="flex justify-center">
      <ArrowDown
        className="text-slate-600"
        size={22}
      />
    </div>
  );
}

function MiddleBlock({
  title,
  icon,
}) {
  return (
    <div className="rounded-xl border border-blue-700 bg-blue-900/20 p-4">

      <div className="flex items-center justify-center gap-3 text-blue-400">

        {icon}

        <span className="font-semibold">
          {title}
        </span>

      </div>

    </div>
  );
}

function Block({
  title,
  value,
  mono = false,
  color,
}) {
  return (
    <div className="rounded-xl border border-slate-700 bg-slate-950 p-4">

      <p className="mb-2 text-sm text-slate-400">
        {title}
      </p>

      <div
        className={`
          break-all
          ${mono ? "font-mono text-xs" : ""}
          ${color}
        `}
      >
        {value || "Waiting..."}
      </div>

    </div>
  );
}