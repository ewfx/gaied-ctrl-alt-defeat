"use client";
import EmlCard from "@/components/classify/EmlCard";
import EmailPdfCard from "@/components/classify/PdfCard";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

export default function Classify() {
  return (
    <div className="flex justify-center items-center">
      <div className="border-2 p-6 min-w-1/2 mt-8 rounded-lg">
      <div className="text-3xl font-medium mb-6">
        Select files to upload
      </div>
        <Tabs defaultValue="pdf" className="" >
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="pdf">PDF + Attachments</TabsTrigger>
            <TabsTrigger value="eml">EML file</TabsTrigger>
          </TabsList>
          <TabsContent value="pdf">
            <EmailPdfCard />
          </TabsContent>
          <TabsContent value="eml">
            <EmlCard />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
