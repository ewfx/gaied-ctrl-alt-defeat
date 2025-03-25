"use client";
import {
    Card,
    CardContent,
    CardFooter,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

export default function ClassifySuccess() {
  const router = useRouter();
  const [data, setData] = useState<Data | null>(null);

  useEffect(() => {
    const successData = localStorage.getItem("successData");
    if (successData) {
      setData(JSON.parse(successData));
    } else {
      router.push("/classify");
    }
  }, [router]);

  if (!data) {
    return null; // or a loading spinner
  }

  interface RequestType {
    request_type: string;
    sub_request_type: string;
    confidence: number;
    reasoning: string;
    is_primary: boolean;
  }

  interface Data {
    request_types: RequestType[];
    support_group: string;
    extracted_fields: {
      field_name: string;
      value: string;
      confidence: number;
      source: string;
    }[];
    is_duplicate: boolean;
    duplicate_reason?: string | null;
    processing_time_ms: number;
    error?: string | null;
  }
  return (
    <div className="flex w-full justify-center items-center">
      <Card className="h-fit min-w-1/2 max-w-10/12 m-8">
        <CardHeader>
          <CardTitle className="text-2xl">Classfication Results</CardTitle>
          <Separator />
        </CardHeader>
        <CardContent className="space-y-4">
          {/* <div className="text-xl font-semibold">Primary Request Type</div>
          <Separator />
          <p>
            {data.request_types[0].request_type} -{" "}
            {data.request_types[0].sub_request_type}
          </p> */}
          <div className="text-xl font-semibold">Support Group  - <i>{data.support_group}</i></div>

          

          <Separator />
          <Table className="border-1">
            {/* <TableCaption>Classification Results</TableCaption> */}
            <TableHeader>
              <TableRow>
                <TableHead className="bg-white/[.05] text-right border-1">
                  Primary
                </TableHead>
                <TableHead className="bg-white/[.05] w-[150px] border-1">
                  Request Type
                </TableHead>
                <TableHead className="bg-white/[.05] border-1">
                  Sub Request Type
                </TableHead>
                <TableHead className="bg-white/[.05] border-1">
                  Confidence
                </TableHead>
                <TableHead className="bg-white/[.05] border-1">
                  Reasoning
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.request_types.map((request, index) => (
                <TableRow key={index}>
                  <TableCell className="text-right border-1">
                    {request.is_primary ? "✅" : "❌"}
                  </TableCell>
                  <TableCell className="font-medium border-1">
                    {request.request_type}
                  </TableCell>
                  <TableCell className="border-1">
                    {request.sub_request_type}
                  </TableCell>
                  <TableCell className="border-1">
                    {(request.confidence * 100).toFixed(2)}%
                  </TableCell>
                  <TableCell className="max-w-md whitespace-normal border-1">
                    {request.reasoning}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
          <div className="text-2xl font-semibold">Fields extracted</div>
          <Separator />

          <Table>
            {/* <TableCaption>Fields extracted</TableCaption> */}
            <TableHeader>
              <TableRow>
                <TableHead className="bg-white/[.05] border-1">
                  Field Name
                </TableHead>
                <TableHead className="bg-white/[.05] border-1">Value</TableHead>
                <TableHead className="bg-white/[.05] border-1">
                  Confidence
                </TableHead>
                <TableHead className="bg-white/[.05] border-1">
                  Source
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.extracted_fields.map((field, index) => (
                <TableRow key={index}>
                  <TableCell className="font-medium border-1">
                    {field.field_name}
                  </TableCell>
                  <TableCell className="border-1">{field.value}</TableCell>
                  <TableCell className="border-1">
                    {(field.confidence * 100).toFixed(2)}%
                  </TableCell>
                  <TableCell className="border-1">{field.source}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
        <CardFooter className="gap-4">
          {/* <Button size="lg" variant={"outline"}>
            Clear Files
          </Button>
          <Button size="lg" variant="default">
            Submit Files
          </Button> */}
        </CardFooter>
      </Card>
    </div>
  );
}
