"use client";

import { useState } from "react";
import { v4 as uuidv4 } from "uuid";
import ChatItem from "./ChatItem";

export default function Chat() {
  const [usersChat, setUsersChat] = useState<
    { id: string; message: string;role:string;time:string}[]
  >([]);
  const [chat, setChat] = useState("");

  const storage = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    if (!chat.trim()) return;

    const newChat = {
      id: uuidv4(),
      message: chat,
      role:"user",
      time: new Date().toLocaleTimeString(),
    };

    setUsersChat(prev => [...prev, newChat]);
    setChat("");
  };

  return (
    <div>
      {usersChat.map(item => (
        <ChatItem key={item.id} detail={item} />
      ))}

     <form
  onSubmit={storage}
  className="fixed bottom-0 left-0 right-0  border-t p-4 flex items-center gap-3"
>
  <input
    type="text"
    value={chat}
    onChange={(e) => setChat(e.target.value)}
    className="flex-1 rounded-full border px-4 py-3 text-black bg-white"
    placeholder="Type a message..."
  />

  <button
    type="submit"
    className="rounded-full bg-blue-600 px-6 py-3 text-white"
  >
    Send
  </button>
</form>
    </div>
  );
}

