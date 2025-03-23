/**
 * v0 by Vercel.
 * @see https://v0.dev/t/aDFucFbMyb8
 * Documentation: https://v0.dev/docs#integrating-generated-code-into-your-nextjs-app
 */
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardFooter } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import React from "react"

interface FileUploadProps {
    onFileChange: (file: File) => void;
    file: File | null;
}

export default function FileUpload(props: FileUploadProps) {
    const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
        event.preventDefault()
        if (event.dataTransfer.files && event.dataTransfer.files[0]) {
            props.onFileChange(event.dataTransfer.files[0])
        }
    }

    const handleDragOver = (event: React.DragEvent<HTMLDivElement>) => {
        event.preventDefault()
    }

    const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        if (event.target.files && event.target.files[0]) {
            props.onFileChange(event.target.files[0])
        }
    }

    return (
        <Card className="h-fit">
            <CardContent className="p-6 space-y-4">
                <div
                    className="border-2 border-dashed border-gray-200 rounded-lg flex flex-col gap-1 p-6 items-center"
                    onDrop={handleDrop}
                    onDragOver={handleDragOver}
                >
                    <FileIcon className="w-12 h-12" />
                    <span className="text-sm font-medium text-gray-500">Drag and drop a file or click to browse</span>
                    <span className="text-xs text-gray-500">PDF, image, video, or audio</span>
                </div>
                <div className="space-y-2 text-sm">
                    <Label htmlFor="file" className="text-sm font-medium">
                        File
                    </Label>
                    <Input id="file" type="file" placeholder="File" accept="image/*" onChange={handleFileChange} />
                </div>
                {props.file && <p className="text-sm text-gray-500">Selected file: {props.file.name}</p>}
            </CardContent>
            <CardFooter>
                <Button size="lg" onClick={() => document.getElementById('file')?.click()}>Upload</Button>
            </CardFooter>
        </Card>
    )
}

interface FileIconProps extends React.SVGProps<SVGSVGElement> {}

function FileIcon(props: FileIconProps) {
    return (
        <svg
            {...props}
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
        >
            <path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z" />
            <path d="M14 2v4a2 2 0 0 0 2 2h4" />
        </svg>
    )
}