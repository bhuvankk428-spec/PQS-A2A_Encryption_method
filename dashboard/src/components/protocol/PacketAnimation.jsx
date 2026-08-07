import { motion } from "framer-motion";

export default function PacketAnimation({
  active,
}) {
  return (
    <div className="relative h-4 w-full">

      <div className="absolute top-1/2 h-px w-full bg-slate-700" />

      {active && (
        <motion.div
          className="absolute top-0 h-4 w-4 rounded-full bg-cyan-400 shadow-lg shadow-cyan-500"
          initial={{ x: 0 }}
          animate={{ x: "100%" }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: "linear",
          }}
        />
      )}

    </div>
  );
}