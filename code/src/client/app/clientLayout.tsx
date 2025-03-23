"use client";
import Dock from "@/components/ui/Dock/Dock";
import {
    ChartArea,
    Home,
    Upload,
    Wrench
} from "lucide-react";
import { useRouter } from "next/navigation";

export default function ClientLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {

    const router = useRouter();
    
    const items = [
    { icon: <Home size={18} />, label: "Home", onClick: () => router.push("/") },
    {
      icon: <Upload size={18} />,
      label: "Upload",
      onClick: () => router.push("/classify"),
    },
    {
      icon: <ChartArea size={18} />,
      label: "Analytics",
      onClick: () => router.push("/analytics"),
    },
    {
      icon: <Wrench size={18} />,
      label: "Configure",
      onClick: () => router.push("/configure"),
    },
  ];
  return (
    <>
      {/* <div className="h-fit">
        <div className="flex items-center justify-between p-4 w-screen">
          <Link href="/" className="flex items-center justify-center">
            <div className="bg-gray-100 rounded-md">
              <Keyboard color="black" className="m-2" />
            </div>
            <h1 className="text-xl font-bold pl-4">Ctrl-Alt-Defeat</h1>
          </Link>
          <div className="flex items-center justify-center">
            <Link href="/configure">
              <Button variant="ghost" size="default" className="mr-4">
                Configure{" "}
              </Button>
            </Link>
            <Separator orientation="vertical" />
            <ModeToggle />
          </div>
        </div>
        <Separator />
      </div> */}
      <div>{children}</div>
      {/* </div> */}
      <div className="absolute bottom-0 left-1/2">
        <Dock
          items={items}
          panelHeight={70}
          baseItemSize={50}
          magnification={70}
          className="fixed"
        />
      </div>
    </>
  );
}
