"use client";
import { backend_uri } from "@/app/Config";
import axios from "axios";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { toast } from "sonner";
import { Button } from "../ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "../ui/card";
import { Input } from "../ui/input";
import { Label } from "../ui/label";
import { LoadingSpinner } from "../ui/LoadingSpinner";
import { Separator } from "../ui/separator";
import { Textarea } from "../ui/textarea";

export default function AddReqForm() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [definition, setDefinition] = useState("");
  const [loading, setLoading] = useState(false);

  type SubRequest = {
    name: string;
    definition: string;
    required_attributes: string[];
  };
  const [subRequests, setSubRequests] = useState<SubRequest[]>([
    { name: "", definition: "", required_attributes: [] },
  ]);

  const addSubRequest = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    setSubRequests([
      ...subRequests,
      { name: "", definition: "", required_attributes: [] },
    ]);
  };
  const removeSubRequest = (
    index: number,
    e: React.MouseEvent<HTMLButtonElement>
  ) => {
    e.preventDefault();
    const newSubRequests = subRequests.filter((_, i) => i !== index);
    setSubRequests(newSubRequests);
  };

  const handleSubRequestChange = (
    index: number,
    field: string,
    value: string | string[]
  ) => {
    const newSubRequests = [...subRequests];
    newSubRequests[index] = { ...newSubRequests[index], [field]: value };
    setSubRequests(newSubRequests);
  };

  const handleSubmit = async () => {
    if (
      !name ||
      !definition ||
      subRequests.some(
        (subReq) =>
          !subReq.name ||
          !subReq.definition ||
          subReq.required_attributes.length === 0
      )
    ) {
      console.error("All fields are required.");
      toast.error("All fields are required.");
      return;
    }

    setLoading(true);

    try {
    const response = await axios.post(`${backend_uri}/request-types/`, {
      name,
      definition,
      sub_request_types: subRequests,
    });
      console.log("submit", response.data);
      toast.success("Request type created successfully.");
      router.push("/configure"); // Redirect to a success page or another route
    } catch (error) {
      console.error("Error submitting form", error);
      toast.error("Error submitting form");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="w-1/2 max-w-2/3 h-fit">
      <CardHeader>
        <CardTitle className="text-2xl">Create Request Type</CardTitle>
        <CardDescription>
          Fill the form and submit to create a request type
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form>
          <div className="grid w-full items-center gap-4">
            <div className="flex flex-col space-y-1.5">
              <Label htmlFor="name">Name</Label>
              <Input
                id="name"
                placeholder="Name of request type"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
            </div>
            <div className="flex flex-col space-y-1.5">
              <Label htmlFor="definition">Definition</Label>
              <Textarea
                id="definition"
                placeholder="Definition of request type"
                value={definition}
                onChange={(e) => setDefinition(e.target.value)}
              />
            </div>
            <Separator />
            <p>Sub request types</p>
            {subRequests.map((subReq, index) => (
              <div key={index}>
                <div key={index} className="flex flex-col space-y-1.5">
                  <Label htmlFor={`subName-${index}`}>Name</Label>
                  <Input
                    id={`subName-${index}`}
                    placeholder="Name of sub request type"
                    value={subReq.name}
                    onChange={(e) =>
                      handleSubRequestChange(index, "name", e.target.value)
                    }
                  />
                  <Label htmlFor={`subDefinition-${index}`}>Definition</Label>
                  <Textarea
                    id={`subDefinition-${index}`}
                    placeholder="Definition of sub request type"
                    value={subReq.definition}
                    onChange={(e) =>
                      handleSubRequestChange(
                        index,
                        "definition",
                        e.target.value
                      )
                    }
                  />
                  <Label htmlFor={`attr-${index}`}>Required Attributes</Label>
                  <Input
                    id={`attr-${index}`}
                    placeholder="Enter comma separated string"
                    value={subReq.required_attributes.join(", ")}
                    onChange={(e) =>
                      handleSubRequestChange(
                        index,
                        "required_attributes",
                        e.target.value.split(",").map((attr) => attr.trim())
                      )
                    }
                  />
                  <Button
                    variant="outline"
                    onClick={(e) => removeSubRequest(index, e)}
                  >
                    Remove
                  </Button>
                </div>
                <Separator className="mt-4" />
              </div>
            ))}
            <Button variant="outline" onClick={addSubRequest}>
              Add Sub Request Type
            </Button>
          </div>
        </form>
      </CardContent>
      <CardFooter className="flex gap-6">
        <Button variant="outline" onClick={() => router.back()}>
          Go back
        </Button>
        <Button onClick={handleSubmit} disabled={loading} >{loading ? <LoadingSpinner /> : "Submit"}</Button>
      </CardFooter>
    </Card>
  );
}
