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

export default function EmailPdfCard() {
  const [emailPdf, setEmailPdf] = useState<File | null>(null);
  const [attachments, setAttachments] = useState<File[]>([]);

  const submitFiles = () => {
    console.log("submit");
    console.log(emailPdf);
    console.log(attachments);
    if (!emailPdf) {
      toast("Upload an email file");
      return;
    }
    const formData = new FormData();
    if (emailPdf) {
      formData.append("email_chain_file", emailPdf);
    }
    attachments.forEach((attachment, index) => {
      formData.append(`attachments[${index}]`, attachment);
    });

    axios
      .post(backend_uri + "/classify-email-chain", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      })
      .then((response) => {
        console.log("Success:", response.data);
        toast("Files submitted successfully");
      })
      .catch((error) => {
        console.error("Error:", error);
        toast("Failed to submit files");
      });
  };

  return (
    <Card className="h-fit">
      <CardHeader>
        <CardTitle className="text-2xl">Upload Email</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {emailPdf ? (
          <div className="flex flex-col items-center space-y-2 border-1 p-4 rounded-md">
            <FileIcon className="w-12 h-12" />
            <span className="text-sm font-medium text-gray-500">
              {emailPdf.name}
            </span>
            <Button
              size="sm"
              variant="destructive"
              onClick={() => {
                setEmailPdf(null);
                toast("File removed");
              }}
            >
              Delete
            </Button>
          </div>
        ) : (
          <Dropzone
            onDrop={(acceptedFiles) => setEmailPdf(acceptedFiles[0] as File)}
            multiple={false}
            accept={{ "application/pdf": [] }}
            onDropRejected={() => toast("Unsupported file type!")}
          >
            {({ getRootProps, getInputProps, isDragActive }) => (
              <section>
                <Label htmlFor="email-pdf" className="text-lg font-medium">
                  Email PDF
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
                    Drop only one pdf file
                  </span>
                  <input {...getInputProps()} className="hidden" />
                </div>
              </section>
            )}
          </Dropzone>
        )}
        <Dropzone
          onDrop={(acceptedFiles) => {
            setAttachments((prev) => [...prev, ...acceptedFiles]);
            if (acceptedFiles.length > 0) toast("Attachments uploaded");
          }}
        >
          {({ getRootProps, getInputProps, isDragActive }) => (
            <section>
              <Label htmlFor="attachments" className="text-lg font-medium">
                Attachments
              </Label>
              <div
                {...getRootProps()}
                className={`border-3 border-dashed rounded-lg flex flex-col gap-1 m-2 p-6 items-center ${
                  isDragActive ? "border-white bg-white/5" : ""
                }`}
              >
                <FileIcon className="w-12 h-12" />
                <span className="text-sm font-medium text-gray-500">
                  Drag and drop files or click to browse
                </span>
                <span className="text-xs text-gray-500">
                  Drop multiple files
                </span>
                <input {...getInputProps()} className="hidden" />
              </div>
            </section>
          )}
        </Dropzone>
        {attachments.length > 0 && (
          <div className="mt-4 space-y-2">
            <div className="text-muted-foreground">Selected files:</div>
            {attachments.map((file, index) => (
              <div
                key={index}
                className="flex items-center space-x-4 border-2 p-4 rounded-md"
              >
                <div className="flex justify-between w-full">
                  <div className="flex items-center justify-center">
                    <FileIcon className="w-8 h-8" />
                    <div className="ml-4 text-sm font-medium text-gray-500">
                      {file.name}
                    </div>
                  </div>
                  <div>
                    <Button
                      size="sm"
                      variant="destructive"
                      onClick={() => {
                        setAttachments((prev) =>
                          prev.filter((_, i) => i !== index)
                        );
                        toast("File removed");
                      }}
                    >
                      Delete
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
      <CardFooter className="gap-4">
        <Button
          size="lg"
          variant={"outline"}
          onClick={() => {
            setEmailPdf(null);
            setAttachments([]);
            toast("All files cleared");
          }}
        >
          Clear Files
        </Button>
        <Button size="lg" variant="default" onClick={submitFiles}>
          Submit Files
        </Button>
      </CardFooter>
    </Card>
  );
}
