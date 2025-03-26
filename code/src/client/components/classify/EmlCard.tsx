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

interface EmlCardProps {
  setChildLoading: (loading: boolean) => void;
}

export default function EmlCard({ setChildLoading }: EmlCardProps) {
  const [emlFile, setEmlFile] = useState<File | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showDupeDialog, setShowDupeDialog] = useState(false);
  const [duplicateData, setDuplicateData] = useState({
    duplicate_confidence: 0,
    duplicate_id: "",
    duplicate_reason: "",
  });

  const router = useRouter();

  const submitFiles = () => {
    if (!emlFile) {
      toast.error("Upload a file!");
      return;
    }
    const formData = new FormData();
    formData.append("eml_file", emlFile);

    setChildLoading(true);
    setIsSubmitting(true);
    axios
      .post(backend_uri + "/classify-eml", formData)
      .then((response) => {
        if (response.data.error !== null) {
          toast.error(`File submission failed! ${response.data.error}`);
        } else if (response.data.is_duplicate && response.data.duplicate_confidence > 0.8) {
          setDuplicateData({
            duplicate_confidence: response.data.duplicate_confidence,
            duplicate_id: response.data.duplicate_id,
            duplicate_reason: response.data.duplicate_reason,
          });
          setShowDupeDialog(true);
        } else {
          toast.success("File submitted successfully!");
          console.log("Success:", response.data);
          localStorage.setItem("successData", JSON.stringify(response.data));
          router.push("/classify/success");
        }
      })
      .catch((error) => {
        toast.error("File submission failed!");
        console.error("Error:", error);
      })
      .finally(() => {
        setChildLoading(false);
        setIsSubmitting(false);
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
              <span className="font-bold">{duplicateData.duplicate_confidence.toFixed(3)}%</span>.
            </p>
            <div className="font-semibold text-lg">Reason:</div> <div> {duplicateData.duplicate_reason}</div>
          </div>
        </DialogContent>
      </Dialog>
    </Card>
  );
}
