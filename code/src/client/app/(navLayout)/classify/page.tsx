"use client";
import EmlCard from "@/components/classify/EmlCard";
import EmailPdfCard from "@/components/classify/PdfCard";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useState } from "react";

export default function Classify() {
  const [childLoading, setChildLoading] = useState(false);
  return (
    <div className="flex justify-center items-center">
      <div className="border-2 p-6 min-w-1/2 mt-8 rounded-lg">
        <div className="text-3xl font-medium mb-6">Select files to upload</div>
        <Tabs defaultValue="pdf" className="">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="pdf" disabled={childLoading}>
              PDF + Attachments
            </TabsTrigger>
            <TabsTrigger value="eml" disabled={childLoading}>
              EML file
            </TabsTrigger>
          </TabsList>
          <TabsContent value="pdf">
            <EmailPdfCard setChildLoading={setChildLoading} />
          </TabsContent>
          <TabsContent value="eml">
            <EmlCard setChildLoading={setChildLoading} />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
