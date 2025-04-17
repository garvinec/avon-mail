import {
  Manrope as FontManrope,
  Lexend as FontSans,
  Newsreader as FontSerif,
} from "next/font/google";

import { cn } from "@/lib/utils";
import { LoginForm } from "@/components/Forms/LoginForm";

const fontSans = FontSans({ subsets: ["latin"], variable: "--font-sans" });
const fontSerif = FontSerif({ subsets: ["latin"], variable: "--font-serif" });
const fontManrope = FontManrope({
  subsets: ["latin"],
  variable: "--font-manrope",
});
export default function LoginPage() {
  const loginImages = [
    "https://images.unsplash.com/photo-1482872376051-5ce74ebf0908?q=80&w=3050&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
    "https://images.unsplash.com/photo-1498758536662-35b82cd15e29?q=80&w=3088&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
    "https://images.unsplash.com/photo-1536147116438-62679a5e01f2?q=80&w=2688&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
  ];

  return (
    <div
      className={cn(
        "flex min-h-screen w-full items-center justify-center p-6",
        fontSans.variable,
        fontSerif.variable,
        fontManrope.variable
      )}
    >
      <div className="theme-login-one w-full max-w-sm md:max-w-3xl">
        <LoginForm
          imageUrl={loginImages[Math.floor(Math.random() * loginImages.length)]}
        />
      </div>
    </div>
  );
}
