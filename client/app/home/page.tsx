"use client";

import { useRouter } from "next/navigation";

export default function Home() {
  const router = useRouter();

  const sendChange = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    try {
      // const response = await fetch("http://localhost:5000/webhook", {
      //   method: "POST",
      //   headers: {
      //     "Content-Type": "application/json",
      //   },
      //   body: JSON.stringify({
      //     message: "Connect request",
      //   }),
      // });

      // const data = await response.json();
      // console.log(data);

      // Redirect after webhook succeeds
      
      router.push("/chat");
      
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="flex h-screen justify-center items-center flex-col gap-4">
      <h1 className="text-4xl font-bold">
        A2A Communications Prototype
      </h1>

      <form onSubmit={sendChange}>
        <button
          type="submit"
          className="px-4 py-2 bg-blue-500 text-white rounded"
        >
          CONNECT
        </button>
      </form>
    </div>
  );
}