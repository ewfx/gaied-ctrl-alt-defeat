"use client";
import BlurText from "@/components/ui/BlurText/BlurText";
import Waves from "@/components/ui/Waves/Waves";
import { GitBranch } from "lucide-react";
import Link from "next/link";
import { useState } from "react";

export default function Home() {
  const [showStuff, setShowStuff] = useState(false);

  const handleAnimationComplete = () => {
    setShowStuff(true);
    return;
  };
  return (
    <div className="relative min-h-screen">
      <div className="absolute inset-0 w-full h-full">
        <Waves
          lineColor="rgba(255,255,255,0.12)"
          backgroundColor="black"
          waveSpeedX={0.02}
          waveSpeedY={0.01}
          waveAmpX={40}
          waveAmpY={20}
          friction={0.9}
          tension={0.01}
          maxCursorMove={120}
          xGap={12}
          yGap={36}
        />
      </div>
      <div className="relative z-10 flex flex-col justify-center items-center min-h-screen">
        <BlurText
          text="Classify Emails Using Gen-AI"
          delay={150}
          animateBy="words"
          direction="top"
          onAnimationComplete={handleAnimationComplete}
          className="text-white text-2xl sm:text-5xl md:text-6xl lg:text-7xl xl:text-8xl font-black mb-8"
          animationFrom={undefined}
          animationTo={undefined}
        />
        <BlurText
          text="A hackathon submission by team Ctrl-Alt-Defeat"
          delay={150}
          animateBy="words"
          direction="top"
          onAnimationComplete={handleAnimationComplete}
          className="text-white text-xs sm:text-xl md:text-2xl lg:text-3xl xl:text-3xl font-mono mb-8"
          animationFrom={undefined}
          animationTo={undefined}
        />
        <Link
          href={"https://github.com/ewfx/gaied-ctrl-alt-defeat/"}
          target="_blank"
          className={
            "text-white flex gap-4 underline w-fit transition-opacity duration-500 delay-200 " +
            (showStuff ? "opacity-100" : "opacity-0")
          }
          id="fadeLink"
        >
          <GitBranch /> open repo
        </Link>
      </div>
    </div>
  );
}
