import { backend_uri } from "@/app/Config";
import { Label } from "@radix-ui/react-label";
import axios from "axios";
import { FileIcon, FileWarning } from "lucide-react";
import { useRouter } from "next/navigation";
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
import { Dialog, DialogContent, DialogTitle } from "../ui/dialog";
import { LoadingSpinner } from "../ui/LoadingSpinner";
import { Separator } from "../ui/separator";

export default function EmailPdfCard({
  setChildLoading,
}: {
  setChildLoading: (loading: boolean) => void;
}) {
  const [emailPdf, setEmailPdf] = useState<File | null>(null);
  const [attachments, setAttachments] = useState<File[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showDupeDialog, setShowDupeDialog] = useState(false);
  const [duplicateData, setDuplicateData] = useState({
    duplicate_confidence: 0,
    duplicate_id: "",
    duplicate_reason: "",
  });

  const router = useRouter();

  const submitFiles = () => {
    if (!emailPdf) {
      toast.error("Upload an email file");
      return;
    }
    setIsSubmitting(true);
    setChildLoading(true);
    const formData = new FormData();

    // Append the main email PDF file
    formData.append("email_chain_file", emailPdf);

    // Append attachments
    attachments.forEach((file) => {
      formData.append("attachments", file);
    });

    axios
      .post(backend_uri + "/classify-email-chain", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      })
      .then((response) => {
        if (response.data.error !== null) {
          toast.error(`File submission failed! ${response.data.error}`);
        } else if (
          response.data.is_duplicate &&
          response.data.duplicate_confidence > 0.8
        ) {
          setDuplicateData({
            duplicate_confidence: response.data.duplicate_confidence,
            duplicate_id: response.data.duplicate_id,
            duplicate_reason: response.data.duplicate_reason,
          });
          setShowDupeDialog(true);
        } else {
          console.log("Success:", response.data);
          localStorage.setItem("successData", JSON.stringify(response.data));
          router.push("/classify/success");

          toast.success("Files submitted successfully");
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        toast.error("Failed to submit files");
      })
      .finally(() => {
        setIsSubmitting(false);
        setChildLoading(false);
      });
  };

  return (
    <>
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
                  toast.warning("File removed");
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
              onDropRejected={() => toast.error("Unsupported file type!")}
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
              if (acceptedFiles.length > 0)
                toast.success("Attachments uploaded");
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
              <div className="text-muted-foreground">Selected attachments:</div>
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
                          toast.warning("File removed");
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
              toast.warning("All files cleared");
            }}
          >
            Clear Files
          </Button>
          <Button size="lg" variant="default" onClick={submitFiles}>
            Submit Files
          </Button>
        </CardFooter>
        <Dialog open={isSubmitting}>
          <DialogContent>
            <DialogTitle />
            <div className="flex flex-col w-full h-full justify-center items-center">
              <LoadingSpinner size={50} />
              <p className="text-md">Submitting...</p>
            </div>
          </DialogContent>
        </Dialog>
        <Dialog open={showDupeDialog} onOpenChange={setShowDupeDialog}>
          <DialogContent>
            <DialogTitle className="flex items-center gap-3">
              <FileWarning /> Duplicate File Detected
            </DialogTitle>
            <Separator />
            <div className="space-y-4">
              <p>
                A duplicate file has been detected with a confidence of{" "}
                <span className="font-bold">
                  {duplicateData.duplicate_confidence.toFixed(3)}
                </span>
                .
              </p>
              <div className="font-semibold text-lg">Reason:</div>{" "}
              <div> {duplicateData.duplicate_reason}</div>
            </div>
          </DialogContent>
        </Dialog>
      </Card>
    </>
  );
}
