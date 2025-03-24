import { backend_uri } from "@/app/Config";
import { Label } from "@radix-ui/react-label";
import axios from "axios";
import { FileIcon } from "lucide-react";
import { useState } from "react";
import Dropzone from "react-dropzone";
import { toast } from "sonner";
import { Button } from "../ui/button";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "../ui/card";

export default function EmlCard() {
  const [emlFile, setEmlFile] = useState<File | null>(null);

  const submitFiles = () => {
    if (!emlFile) {
      toast.error("Upload a file!");
      return;
    }
    const formData = new FormData();
    formData.append("eml_file", emlFile);

    axios
      .post(backend_uri + "/classify-eml", formData)
      .then((response) => {
        toast.success("File submitted successfully!");
        console.log("Success:", response.data);
      })
      .catch((error) => {
        toast.success("File submission failed!");
        console.error("Error:", error);
      });
  };

  return (
    <Card className="h-fit">
      <CardHeader>
        <CardTitle className="text-2xl">Upload EML File</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {emlFile ? (
          <div className="flex flex-col items-center space-y-2 border-2 p-4 rounded-md">
            <FileIcon className="w-12 h-12" />
            <span className="text-sm font-medium text-gray-500">
              {emlFile.name}
            </span>
            <Button
              size="sm"
              variant="destructive"
              onClick={() => {
                setEmlFile(null);
                toast.warning("File removed");
              }}
            >
              Delete
            </Button>
          </div>
        ) : (
          <Dropzone
            onDrop={(acceptedFiles) => setEmlFile(acceptedFiles[0] as File)}
            multiple={false}
            accept={{ "message/rfc822": [] }}
            onDropRejected={() => toast.error("Unsupported file type!")}
          >
            {({ getRootProps, getInputProps, isDragActive }) => (
              <section>
                <Label htmlFor="email-pdf" className="text-lg font-medium">
                  Upload EML file
                </Label>
                <div
                  {...getRootProps()}
                  className={`border-3 border-dashed rounded-lg flex flex-col gap-1 m-2 p-6 items-center ${
                    isDragActive ? "border-white bg-white/5" : ""
                  }`}
                >
                  <FileIcon className="w-12 h-12" />
                  <span className="text-sm font-medium text-gray-500">
                    Drag and drop a file or click to browse
                  </span>
                  <span className="text-xs text-gray-500">
                    Drop only one EML file
                  </span>
                  <input {...getInputProps()} className="hidden" />
                </div>
              </section>
            )}
          </Dropzone>
        )}
      </CardContent>
      <CardFooter>
        <Button size="lg" onClick={submitFiles}>
          Submit Files
        </Button>
      </CardFooter>
    </Card>
  );
}
