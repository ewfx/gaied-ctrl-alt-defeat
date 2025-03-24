"use client";
import Dock from "@/components/ui/Dock/Dock";
import { ChartArea, Home, Upload, Wrench } from "lucide-react";
import { useRouter } from "next/navigation";

export default function DockLayoutComponent({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const router = useRouter();

  const items = [
    {
      icon: <Home size={30} />,
      label: "Home",
      onClick: () => router.push("/"),
    },
    {
      icon: <Upload size={30} />,
      label: "Upload",
      onClick: () => router.push("/classify"),
    },
    {
      icon: <ChartArea size={30} />,
      label: "Analytics",
      onClick: () => router.push("/analytics"),
    },
    {
      icon: <Wrench size={30} />,
      label: "Configure",
      onClick: () => router.push("/configure"),
    },
  ];
  return (
    <>
      <div>{children}</div>
      <div className="absolute h-0">
        <Dock
          items={items}
          panelHeight={100}
          baseItemSize={80}
          magnification={100}
          className="fixed z-50 bg-black"
        />
      </div>
    </>
  );
}
