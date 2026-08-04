type ChatItemProps = {
  detail: {
    id: string;
    message: string;
    role: string;
    time: Date | string;
  };
};

export default function ChatItem({ detail }: ChatItemProps) {
  const isUser = detail.role === "user";

  return (
    <div className={`flex mb-3 ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-sm rounded-xl px-4 py-2 shadow-md ${
          isUser
            ? "bg-white text-black"
            : "bg-red-500 text-white"
        }`}
      >
        <p>{detail.message}</p>

        <p className="mt-1 text-xs opacity-70 text-right">
          {typeof detail.time === "string"
            ? detail.time
            : detail.time.toLocaleTimeString()}
        </p>
      </div>
    </div>
  );
}