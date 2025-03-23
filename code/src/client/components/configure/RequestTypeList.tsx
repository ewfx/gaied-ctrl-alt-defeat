import { Pencil, Plus, Trash } from "lucide-react";
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

export default function RequestTypeList() {
  const mockData = [
    {
      _id: "67dfcad1d8ce3bea5d93ac89",
      name: "Loan Adjustment",
      definition:
        "Request to adjust loan terms.Request to adjust loan terms.Request to adjust loan terms.Request to adjust loan terms.Request to adjust loan terms.Request to adjust loan terms.Request to adjust loan terms.Request to adjust loan terms.Request to adjust loan terms.Request to adjust loan terms.",
      sub_request_types: [
        {
          id: "67dfcadcd8ce3bea5d93ac8a",
          name: "Interest Rate Change",
          definition: "Request to change interest rate.",
          required_attributes: ["new_rate", "effective_date"],
        },
        {
          id: "67dfcadfd8ce3bea5d93ac8b",
          name: "Interest Rate Change2",
          definition: "Request to change interest rate.",
          required_attributes: ["new_rate", "effective_date"],
        },
      ],
    },
    {
      _id: "67dfcaedd8ce3bea5d93ac8c",
      name: "Loan Adjustment2",
      definition: "Request to adjust loan terms.",
      sub_request_types: [
        {
          id: "67dfcaf5d8ce3bea5d93ac8d",
          name: "Interest Rate Change2",
          definition: "Request to change interest rate.",
          required_attributes: ["new_rate", "effective_date"],
        },
        {
          id: "67dfcaf8d8ce3bea5d93ac8e",
          name: "Interest Rate Change",
          definition: "Request to change interest rate.",
          required_attributes: ["new_rate", "effective_date"],
        },
      ],
    },
  ];

  return (
    <Card className="w-1/2 max-w-2/3 h-fit">
      <CardHeader>
        <CardTitle className="text-xl">Request Types</CardTitle>
        <CardDescription>
          View the different request types used for classification.
        </CardDescription>
        <Button className="mt-4">Add a new Request type</Button>
      </CardHeader>
      <CardContent>
        <div className="grid w-full items-center gap-4">
          <Accordion type="single" collapsible className="w-full" id="reqType">
            {mockData.map((reqType, index) => {
              return (
                <AccordionItem key={reqType._id} value={reqType._id} className="">
                  <AccordionTrigger className="text-lg">
                    {reqType.name}
                  </AccordionTrigger>
                  <AccordionContent className="border-l-1 pl-3">
                    <div className="flex w-full items-center gap-4">
                      <Button variant={"outline"} size={"default"} className="mb-4">
                        <Pencil /> Edit
                      </Button>
                      <Button
                        variant={"destructive"}
                        size={"default"}
                        className="mb-4"
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
                      <Button variant={"outline"} size={"sm"} className="">
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
                                >
                                  <Pencil /> Edit
                                </Button>
                                <Button
                                  variant={"destructive"}
                                  size={"sm"}
                                  className="mb-4"
                                >
                                  <Trash /> Delete
                                </Button>
                              </div>
                              <p>{subReq.definition}</p>
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
        </div>
      </CardContent>
    </Card>
  );
}
