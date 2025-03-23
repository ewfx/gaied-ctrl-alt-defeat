"use client";
import { backend_uri } from "@/app/Config";
import axios from "axios";
import { ArrowLeft, ChevronRight, Pencil, Trash } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { toast } from "sonner";
import {
    Accordion,
    AccordionContent,
    AccordionItem,
    AccordionTrigger,
} from "../ui/accordion";
import { Button } from "../ui/button";
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "../ui/card";
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle
} from "../ui/dialog";
import { Input } from "../ui/input";
import { Label } from "../ui/label";
import { Popover, PopoverContent, PopoverTrigger } from "../ui/popover";
import { Separator } from "../ui/separator";
import { Skeleton } from "../ui/skeleton";
import { Textarea } from "../ui/textarea";

export default function RequestTypeList() {
  type SubRequestType = {
    _id: string;
    name: string;
    definition: string;
    required_attributes: string[];
  };

  type RequestType = {
    _id: string;
    name: string;
    definition: string;
    sub_request_types: SubRequestType[];
  };
  const [data, setData] = useState<RequestType[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedReq, setSelectedReq] = useState<RequestType | null>();
  const [editReq, setEditReq] = useState<RequestType | null>(null);
  const [editSubReq, setEditSubReq] = useState<SubRequestType | null>(null);
  const [deletePopOpen, setDeletePopOpen] = useState<boolean>(false);
  const [deleteSubPopOpen, setDeleteSubPopOpen] = useState<boolean>(false);
  const [showReqTypeDialog, setShowReqTypeDialog] = useState<boolean>(false);
  const [showSubReqTypeDialog, setShowSubReqTypeDialog] =
    useState<boolean>(false);

  const router = useRouter();

  const fetchData = async () => {
    try {
      setLoading(true);
      const response = await axios.get(backend_uri + "/request-types/");
      setData(response.data);
      setLoading(false);
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const submitEditRequest = () => {
    if (editReq) {
        axios
            .put(`${backend_uri}/request-types/${editReq._id}`, editReq)
            .then(() => {
                toast("Request type updated successfully");
                setShowReqTypeDialog(false);
                setSelectedReq(null)
                fetchData();
            })
            .catch((error) => {
                console.error("Error updating request type:", error);
            });
    }
  }

  const handleSelect = (reqType: RequestType) => {
    setSelectedReq(reqType);
  };

  const handleEditRequest = (requestType: RequestType) => {
    setEditReq(requestType)
    // console.log("editreq", reqId);
    router.push("/editReq/"+requestType._id)
  };

  const handleDeleteRequest = (reqId: string) => {
    setDeletePopOpen(false);
    console.log("deletereq", reqId);
    axios
      .delete(`${backend_uri}/request-types/${reqId}`)
      .then(() => {
        toast("Deleted succesfully");
        setSelectedReq(null);
        fetchData();
      })
      .catch((error) => {
        console.error("Error deleting request type:", error);
      });
  };

  const handleEditSubRequest = (reqId: string) => {
    console.log("editsub", reqId);
  };

  const handleDeleteSubRequest = (reqId: string, subreqId: string) => {
    setDeleteSubPopOpen(false);
    console.log("deletereq", subreqId);
    axios
      .delete(
        `${backend_uri}/request-types/${reqId}/sub-request-types/${subreqId}`
      )
      .then(() => {
        toast("Deleted succesfully");
        setSelectedReq(null);
        fetchData();
      })
      .catch((error) => {
        console.error("Error deleting request type:", error);
      });
  };

  const handleAddRequest = () => {
    router.push("/addReq");
  };

  const handleAddSubRequest = (reqId: string) => {
    console.log("addsubreq", reqId);
  };

  return (
    <Card className="min-w-1/2 h-fit">
      <CardHeader>
        <CardTitle className="text-2xl">Configure Request Types</CardTitle>
        <CardDescription>
          View the different request types used for classification.
        </CardDescription>
        <Separator className="mt-4" />
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-[1fr_2fr] gap-2 p-4">
          <div>
            <p className="text-2xl mb-0">Request Types</p>
            <div className="text-muted-foreground mb-2 text-sm">
              Select a request to view the details
            </div>
            <Button className="mt-4" onClick={handleAddRequest}>
              Add a new Request type
            </Button>
            {loading ? (
              <div className="flex flex-col space-y-3 mt-6">
                <div className="space-y-6">
                  <Skeleton className="h-4 w-full" />
                  <Skeleton className="h-4 w-[250px]" />
                  <Skeleton className="h-4 w-full" />
                  <Skeleton className="h-4 w-[200px]" />
                </div>
              </div>
            ) : (
              data.map((reqType, index) => {
                return (
                  <div key={index}>
                    <Button
                      size={"lg"}
                      variant={"ghost"}
                      className="w-full text-left mb-4 mt-4 cursor-pointer flex justify-between rounded-b-none rounded-none"
                      onClick={() => handleSelect(reqType)}
                    >
                      {reqType.name}
                      <ChevronRight />
                    </Button>
                    <Separator className="" />
                  </div>
                );
              })
            )}
          </div>
          <div className="border-l-1 p-6">
            {selectedReq ? (
              <>
                <div className="flex justify-between">
                  <div>
                    <p className="text-2xl mb-2">{selectedReq.name}</p>
                  </div>
                  <div className="flex gap-4">
                    <Button
                      variant={"outline"}
                      size={"default"}
                      className="mb-4"
                      onClick={() => handleEditRequest(selectedReq)}
                    >
                      <Pencil /> Edit
                    </Button>
                    <Popover
                      open={deletePopOpen}
                      onOpenChange={(e) => setDeletePopOpen(e)}
                    >
                      <PopoverTrigger asChild>
                        <Button
                          variant={"destructive"}
                          size={"default"}
                          className="mb-4"
                        >
                          <Trash /> Delete
                        </Button>
                      </PopoverTrigger>
                      <PopoverContent className="w-80">
                        <div className="flex flex-col items-center">
                          <p>
                            Are you sure you want to delete this request type?
                          </p>
                          <div className="flex gap-2 mt-4">
                            <Button
                              variant={"destructive"}
                              size={"default"}
                              onClick={() =>
                                handleDeleteRequest(selectedReq._id)
                              }
                            >
                              Delete
                            </Button>

                            <Button
                              variant={"outline"}
                              size={"default"}
                              onClick={() => setDeletePopOpen(false)}
                            >
                              Cancel
                            </Button>
                          </div>
                        </div>
                      </PopoverContent>
                    </Popover>
                  </div>
                </div>

                <Separator className="mb-4" />
                <p className="text-lg mb-2 font-bold">Definition:</p>

                <p className="pl-2 mb-4 ">{selectedReq.definition}</p>

                <Separator className="mb-4" />

                <p className="text-lg mb-2 font-bold">Sub request types:</p>

                <Accordion
                  type="single"
                  collapsible
                  className="pl-2"
                  id="reqType"
                >
                  {selectedReq.sub_request_types.map((subReq, index) => {
                    return (
                      subReq.name && (
                        <AccordionItem key={subReq._id} value={subReq._id}>
                          <AccordionTrigger>{subReq.name}</AccordionTrigger>
                          <AccordionContent className="border-l-1 pl-3">
                            <p>{subReq.definition}</p>
                            <p className="mt-2 font-bold">
                              Required attributes:
                            </p>
                            {subReq.required_attributes.join(", ")}
                          </AccordionContent>
                        </AccordionItem>
                      )
                    );
                  })}
                </Accordion>
              </>
            ) : (
              <div className="flex justify-center items-center w-full h-full text-2xl gap-4">
                <ArrowLeft /> Select a request to view its details
              </div>
            )}
          </div>
        </div>
      </CardContent>
      <Dialog
        open={showReqTypeDialog}
        onOpenChange={(e) => setShowReqTypeDialog(e)}
      >
        <DialogContent className="max-h-80">
          <DialogHeader>
            <DialogTitle>Edit Request Type</DialogTitle>
            <DialogContent>
            <form>
                <div className="grid w-full items-center gap-4">
                    <div className="flex flex-col space-y-1.5">
                        <Label htmlFor="name">Name</Label>
                        <Input
                            id="name"
                            placeholder="Name of request type"
                            value={editReq?.name || ""}
                            onChange={(e) =>
                                setEditReq({ ...editReq, name: e.target.value } as RequestType)
                            }
                        />
                    </div>
                    <div className="flex flex-col space-y-1.5">
                        <Label htmlFor="definition">Definition</Label>
                        <Textarea
                            id="definition"
                            placeholder="Definition of request type"
                            value={editReq?.definition || ""}
                            onChange={(e) =>
                                setEditReq({ ...editReq, definition: e.target.value } as RequestType)
                            }
                        />
                    </div>
                    <Separator />
                    <p>Sub request types</p>
                    <div className="max-h-96">
                    {editReq?.sub_request_types.map((subReq, index) => (
                        <div key={index}>
                            <div key={index} className="flex flex-col space-y-1.5">
                                <Label htmlFor={`subName-${index}`}>Name</Label>
                                <Input
                                    id={`subName-${index}`}
                                    placeholder="Name of sub request type"
                                    value={subReq.name}
                                    onChange={(e) => {
                                        const newSubRequests = [...editReq.sub_request_types];
                                        newSubRequests[index] = {
                                            ...newSubRequests[index],
                                            name: e.target.value,
                                        };
                                        setEditReq({
                                            ...editReq,
                                            sub_request_types: newSubRequests,
                                        } as RequestType);
                                    }}
                                />
                                <Label htmlFor={`subDefinition-${index}`}>Definition</Label>
                                <Textarea
                                    id={`subDefinition-${index}`}
                                    placeholder="Definition of sub request type"
                                    value={subReq.definition}
                                    onChange={(e) => {
                                        const newSubRequests = [...editReq.sub_request_types];
                                        newSubRequests[index] = {
                                            ...newSubRequests[index],
                                            definition: e.target.value,
                                        };
                                        setEditReq({
                                            ...editReq,
                                            sub_request_types: newSubRequests,
                                        } as RequestType);
                                    }}
                                />
                                <Label htmlFor={`attr-${index}`}>Required Attributes</Label>
                                <Input
                                    id={`attr-${index}`}
                                    placeholder="Enter comma separated string"
                                    value={subReq.required_attributes.join(", ")}
                                    onChange={(e) => {
                                        const newSubRequests = [...editReq.sub_request_types];
                                        newSubRequests[index] = {
                                            ...newSubRequests[index],
                                            required_attributes: e.target.value
                                                .split(",")
                                                .map((attr) => attr.trim()),
                                        };
                                        setEditReq({
                                            ...editReq,
                                            sub_request_types: newSubRequests,
                                        } as RequestType);
                                    }}
                                />
                                <Button
                                    variant="destructive"
                                    onClick={(e) => {
                                        e.preventDefault()
                                        const newSubRequests = editReq.sub_request_types.filter(
                                            (_, i) => i !== index
                                        );
                                        setEditReq({
                                            ...editReq,
                                            sub_request_types: newSubRequests,
                                        } as RequestType);
                                    }}
                                >
                                    Remove Sub Request Type
                                </Button>
                            </div>
                            <Separator className="mt-4" />
                        </div>
                    ))}
                    </div>
                    <Button
                        variant="outline"
                        onClick={(e) => {
                            e.preventDefault()
                            const newSubRequests = [
                                ...(editReq?.sub_request_types || []),
                                { _id: "", name: "", definition: "", required_attributes: [] },
                            ];
                            setEditReq({
                                ...editReq,
                                sub_request_types: newSubRequests,
                            } as RequestType);
                        }}
                    >
                        Add Sub Request Type
                    </Button>
                </div>
                <div className="flex justify-end gap-4 mt-4">
                    <Button
                        variant="outline"
                        onClick={(e) => {
                            e.preventDefault();
                            setShowReqTypeDialog(false)
                        }}
                    >
                        Cancel
                    </Button>
                    <Button
                        onClick={(e) => {
                            // Add your submit logic here
                            e.preventDefault()
                            submitEditRequest()
                        }}
                    >
                        Save
                    </Button>
                </div>
            </form>
            </DialogContent>
          </DialogHeader>
        </DialogContent>
      </Dialog>
    </Card>
  );
}
