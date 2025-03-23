"use client";
import { backend_uri } from "@/app/Config";
import axios from "axios";
import { Pencil, Plus, Trash } from "lucide-react";
import { useEffect, useState } from "react";
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
import { Skeleton } from "../ui/skeleton";

export default function RequestTypeList() {
  type SubRequestType = {
    id: string;
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

  const fetchData = async () => {
    try {
      setLoading(true);
      const response = await axios.get(backend_uri + "/reqtypes/");
      setData(response.data);
      setLoading(false);
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  };
  useEffect(() => {
    fetchData();
  }, []);

  const handleEditRequest = (reqId: string) => {
    console.log("editreq", reqId);
  };

  const handleDeleteRequest = (reqId: string) => {
    console.log("deletereq", reqId);
  };

  const handleEditSubRequest = (reqId: string) => {
    console.log("editsub", reqId);
  };

  const handleDeleteSubRequest = (reqId: string) => {
    console.log("deletesub", reqId);
  };

  const handleAddRequest = () => {
    console.log("addreq");
  };

  const handleAddSubRequest = (reqId: string) => {
    console.log("addsubreq", reqId);
  };

  return (
    <Card className="w-1/2 max-w-2/3 h-fit">
      <CardHeader>
        <CardTitle className="text-xl">Request Types</CardTitle>
        <CardDescription>
          View the different request types used for classification.
        </CardDescription>
        <Button className="mt-4" onClick={handleAddRequest}>
          Add a new Request type
        </Button>
      </CardHeader>
      <CardContent>
        <div className="grid w-full items-center gap-4">
          {loading ? (
            <div className="flex flex-col space-y-3 mt-3">
            <div className="space-y-6">
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-[250px]" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-[200px]" />
            </div>
          </div>
          ) : (
            <Accordion
              type="single"
              collapsible
              className="w-full"
              id="reqType"
            >
              {data.map((reqType, index) => {
                return (
                  <AccordionItem
                    key={reqType._id}
                    value={reqType._id}
                    className=""
                  >
                    <AccordionTrigger className="text-lg">
                      {reqType.name}
                    </AccordionTrigger>
                    <AccordionContent className="border-l-1 pl-3">
                      <div className="flex w-full items-center gap-4">
                        <Button
                          variant={"outline"}
                          size={"default"}
                          className="mb-4"
                          onClick={() => handleEditRequest(reqType._id)}
                        >
                          <Pencil /> Edit
                        </Button>
                        <Button
                          variant={"destructive"}
                          size={"default"}
                          className="mb-4"
                          onClick={() => handleDeleteRequest(reqType._id)}
                        >
                          <Trash /> Delete
                        </Button>
                      </div>
                      <p className="text-lg mb-1 font-semibold">Definition:</p>
                      <p className="">{reqType.definition}</p>

                      <div className="flex justify-between items-end">
                        <p className="text-lg mt-3 mb-1 font-semibold">
                          Sub Request Types:
                        </p>
                        <Button
                          variant={"outline"}
                          size={"sm"}
                          onClick={() => handleAddSubRequest(reqType._id)}
                        >
                          <Plus /> Add
                        </Button>
                      </div>

                      <Accordion
                        type="single"
                        collapsible
                        className="pl-6"
                        id="reqType"
                      >
                        {reqType.sub_request_types.map((subReq, index) => {
                          return (
                            <AccordionItem key={subReq.id} value={subReq.id}>
                              <AccordionTrigger>{subReq.name}</AccordionTrigger>
                              <AccordionContent className="border-l-1 pl-3">
                                <div className="flex w-full items-center gap-4">
                                  <Button
                                    variant={"outline"}
                                    size={"sm"}
                                    className="mb-4"
                                    onClick={() =>
                                      handleEditSubRequest(subReq.id)
                                    }
                                  >
                                    <Pencil /> Edit
                                  </Button>
                                  <Button
                                    variant={"destructive"}
                                    size={"sm"}
                                    className="mb-4"
                                    onClick={() =>
                                      handleDeleteSubRequest(subReq.id)
                                    }
                                  >
                                    <Trash /> Delete
                                  </Button>
                                </div>
                                <p>{subReq.definition}</p>
                                <p className="mt-2 font-bold">
                                  Required attributes:
                                </p>
                                {subReq.required_attributes.join(", ")}
                              </AccordionContent>
                            </AccordionItem>
                          );
                        })}
                      </Accordion>
                    </AccordionContent>
                  </AccordionItem>
                );
              })}
            </Accordion>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
