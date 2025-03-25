"use client";
import { backend_uri } from "@/app/Config";
import axios from "axios";
import { ArrowLeft, ChevronRight, Pencil, Plus, Trash } from "lucide-react";
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
import { LoadingSpinner } from "../ui/LoadingSpinner";
import { Popover, PopoverContent, PopoverTrigger } from "../ui/popover";
import { Separator } from "../ui/separator";
import { Skeleton } from "../ui/skeleton";

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
    support_group: string;
    sub_request_types: SubRequestType[];
  };
  const [data, setData] = useState<RequestType[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedReq, setSelectedReq] = useState<RequestType | null>();
  const [deletePopOpen, setDeletePopOpen] = useState<boolean>(false);
  const [addLoading, setAddLoading] = useState<boolean>(false);
  const [editLoading, setEditLoading] = useState<boolean>(false);
  const [deleteLoading, setDeleteLoading] = useState<boolean>(false);

  const router = useRouter();

  const fetchData = async () => {
    try {
      setLoading(true);
      const response = await axios.get(backend_uri + "/request-types/");
      setData(response.data);
      setLoading(false);
    } catch (error) {
      toast.error("something went wrong");
      setLoading(false);
      console.error("Error fetching data:", error);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleSelect = (reqType: RequestType) => {
    setSelectedReq(reqType);
  };

  const handleEditRequest = (requestType: RequestType) => {
    setEditLoading(true);
    router.push("/editReq/" + requestType._id);
  };

  const handleDeleteRequest = (reqId: string) => {
    setDeletePopOpen(false);
    setDeleteLoading(true);
    console.log("deletereq", reqId);
    axios
      .delete(`${backend_uri}/request-types/${reqId}`)
      .then(() => {
        toast.success("Deleted succesfully");
        setSelectedReq(null);
        fetchData();
      })
      .catch((error) => {
        console.error("Error deleting request type:", error);
      })
      .finally(() => setDeleteLoading(false));
  };

  const handleAddRequest = () => {
    setAddLoading(true);
    router.push("/addReq");
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
            <div className="w-full flex justify-between items-center">
              <div>
                <p className="text-2xl mb-0">Request Types</p>
                <div className="text-muted-foreground mb-2 text-sm">
                  Select a request to view the details
                </div>
              </div>
              <div>
                <Button
                  variant={"outline"}
                  className="mb-1 ml-2"
                  onClick={handleAddRequest}
                  disabled={addLoading}
                >
                  {addLoading ? (
                    <>
                      <LoadingSpinner /> Loading
                    </>
                  ) : (
                    <>
                      <Plus />
                      Add
                    </>
                  )}
                </Button>
              </div>
            </div>
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
                      disabled={editLoading}
                      onClick={() => handleEditRequest(selectedReq)}
                    >
                      {editLoading ? (
                        <>
                          <LoadingSpinner /> Loading
                        </>
                      ) : (
                        <>
                          <Pencil /> Edit
                        </>
                      )}
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
                          disabled={deleteLoading}
                        >
                          {deleteLoading ? (
                            <>
                              <LoadingSpinner /> Loading
                            </>
                          ) : (
                            <>
                              <Trash /> Delete
                            </>
                          )}
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
                <p className="text-lg mb-2 font-bold">Support Group:</p>

                <p className="pl-2 mb-4 ">{selectedReq.support_group}</p>

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
                            <p className="mt-2 font-bold">Definition:</p>
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
    </Card>
  );
}
