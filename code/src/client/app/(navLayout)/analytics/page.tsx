"use client";

import { backend_uri } from "@/app/Config";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  ChartConfig,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart";
import { LoadingSpinner } from "@/components/ui/LoadingSpinner";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import axios from "axios";
import { useEffect, useState } from "react";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Label,
  Pie,
  PieChart,
  XAxis,
  YAxis,
} from "recharts";

// const data = [
//   {
//     _id: "67e2fe91fa5cefc8eec15603",
//     request_type: "Adjustment",
//     sub_request_type: "Reallocation Fees",
//     confidence: 0.95,
//     support_group: "Loan Adjustments Team",
//     timestamp: "2025-03-26T00:35:53.616532",
//   },
//   {
//     _id: "67e2ff660ffabf8e6f795f43",
//     request_type: "Adjustment",
//     sub_request_type: "Other",
//     confidence: 0.95,
//     support_group: "Loan Adjustments Team",
//     timestamp: "2025-03-26T00:39:26.900013",
//   },
//   {
//     _id: "67e300e9815e03c4ea606ecc",
//     request_type: "Closing Notice",
//     sub_request_type: "Amendment Fees",
//     confidence: 0.98,
//     support_group: "Banking Operations Team",
//     timestamp: "2025-03-26T00:45:53.081658",
//   },
//   {
//     _id: "67e30106815e03c4ea606ecd",
//     request_type: "AU Transfer",
//     sub_request_type: "Internal account transfer",
//     confidence: 0.95,
//     support_group: "Cash Management Team",
//     timestamp: "2025-03-26T00:46:22.887084",
//   },
// ];

const chartConfig = {
  value: {
    label: "Value",
    color: "hsl(var(--chart-1))",
  },
} satisfies ChartConfig;

const Dashboard = () => {
  interface RequestData {
    _id: string;
    request_type: string;
    sub_request_type: string;
    confidence: number;
    support_group: string;
    timestamp: string;
  }

  const [data, setData] = useState<RequestData[]>([]);
  const [dataLoaded, setDataLoaded] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get(backend_uri + "/analytics");
        if (Array.isArray(response.data)) {
          setData(response.data);

          // Calculate total requests
          setTotalRequests(response.data.length);

          // Calculate request type count
          const requestTypeCount = Object.entries(
            response.data.reduce((acc, { request_type }) => {
              acc[request_type] = (acc[request_type] || 0) + 1;
              return acc;
            }, {} as Record<string, number>)
          ).map(([name, value]) => ({ name, value: value as number }));
          setRequestTypeCount(requestTypeCount);

          // Calculate request type chart config
          const requestTypeChartConfig = requestTypeCount.reduce(
            (acc, { name }, index) => {
              acc[name] = {
                label: name,
                color: `hsl(var(--chart-${(index % 5) + 1}))`,
              };
              return acc;
            },
            {} as ChartConfig
          );
          setRequestTypeChartConfig(requestTypeChartConfig);

          // Calculate support group count
          const supportGroupCount = Object.entries(
            response.data.reduce((acc, { support_group }) => {
              acc[support_group] = (acc[support_group] || 0) + 1;
              return acc;
            }, {} as Record<string, number>)
          ).map(([name, value]) => ({ name, value: value as number }));
          setSupportGroupCount(supportGroupCount);

          // Calculate confidence data
          const confidenceData = response.data.map((req) => ({
            name: req.request_type,
            confidence: req.confidence,
          }));
          setConfidenceData(confidenceData);
          // Calculate requests per day
          const requestsPerDay = Object.entries(
            response.data.reduce((acc, { timestamp }) => {
              const date = new Date(timestamp).toLocaleDateString();
              acc[date] = (acc[date] || 0) + 1;
              return acc;
            }, {} as Record<string, number>)
          ).map(([date, count]) => ({ date, count: count as number }));
          setRequestsPerDay(requestsPerDay);
          setDataLoaded(true);
        } else {
          console.error("Fetched data is not an array:", response.data);
        }
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };

    fetchData();
  }, []);

  const [totalRequests, setTotalRequests] = useState(0);
  const [requestTypeCount, setRequestTypeCount] = useState<
    { name: string; value: number }[]
  >([]);
  const [requestsPerDay, setRequestsPerDay] = useState<
    { date: string; count: number }[]
  >([]);
  const [requestTypeChartConfig, setRequestTypeChartConfig] =
    useState<ChartConfig>({});
  const [supportGroupCount, setSupportGroupCount] = useState<
    { name: string; value: number }[]
  >([]);
  const [confidenceData, setConfidenceData] = useState<
    { name: string; confidence: number }[]
  >([]);

  return (
    <>
      {dataLoaded ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 p-4">
          {/* Request Type Distribution */}
          <Card>
            <CardHeader>
              <CardTitle className="text-2xl">
                Request Type Distribution
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ChartContainer
                config={requestTypeChartConfig}
                className="mx-auto aspect-square max-h-[700px]"
              >
                <PieChart>
                  <ChartTooltip
                    cursor={false}
                    content={<ChartTooltipContent hideLabel />}
                  />
                  <Pie
                    data={requestTypeCount}
                    dataKey="value"
                    nameKey="name"
                    innerRadius={70}
                    strokeWidth={5}
                    label={({ name, value }) => `${name}: ${value}`}
                    labelLine={false}
                  >
                    {requestTypeCount.map((entry, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={`hsl(var(--chart-${(index % 5) + 1}))`}
                      />
                    ))}
                    <Label
                      content={({ viewBox }) => {
                        if (viewBox && "cx" in viewBox && "cy" in viewBox) {
                          return (
                            <text
                              x={viewBox.cx}
                              y={viewBox.cy}
                              textAnchor="middle"
                              dominantBaseline="middle"
                            >
                              <tspan
                                x={viewBox.cx}
                                y={viewBox.cy}
                                className="fill-foreground text-3xl font-bold"
                              >
                                {totalRequests.toLocaleString()}
                              </tspan>
                              <tspan
                                x={viewBox.cx}
                                y={(viewBox.cy || 0) + 24}
                                className="fill-muted-foreground"
                              >
                                Requests
                              </tspan>
                            </text>
                          );
                        }
                      }}
                    />
                  </Pie>
                </PieChart>
              </ChartContainer>
            </CardContent>
          </Card>

          {/* Support Group Workload */}
          <Card>
            <CardHeader>
              <CardTitle className="text-2xl">Support Group Workload</CardTitle>
            </CardHeader>
            <CardContent>
              <ChartContainer config={chartConfig}>
                <BarChart accessibilityLayer data={supportGroupCount}>
                  <CartesianGrid vertical={false} />
                  <XAxis dataKey="name" tickLine={false} tickMargin={10} />
                  <YAxis />
                  <ChartTooltip
                    cursor={false}
                    content={<ChartTooltipContent hideLabel />}
                  />
                  <Bar dataKey="value" radius={10}>
                    {supportGroupCount.map((_, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={`hsl(var(--chart-${(index % 5) + 1}))`}
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ChartContainer>
            </CardContent>
          </Card>

          {/* Requests Per Day */}
          <Card>
            <CardHeader>
              <CardTitle className="text-2xl">Requests Per Day</CardTitle>
            </CardHeader>
            <CardContent>
              <ChartContainer config={chartConfig}>
                <BarChart data={requestsPerDay}>
                  <CartesianGrid vertical={false} />
                  <XAxis dataKey="date" tickLine={false} tickMargin={10} />
                  <YAxis />
                  <ChartTooltip
                    cursor={false}
                    content={<ChartTooltipContent hideLabel />}
                  />
                  <Bar dataKey="count" radius={10}>
                    {requestsPerDay.map((_, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={`hsl(var(--chart-${(index % 5) + 1}))`}
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ChartContainer>
            </CardContent>
          </Card>

          {/* Confidence Levels */}
          <Card className="">
            <CardHeader>
              <CardTitle className="text-2xl">Confidence Levels</CardTitle>
            </CardHeader>
            <CardContent>
              <ChartContainer
                config={chartConfig}
                className="min-h-[200px] w-full"
              >
                <AreaChart data={confidenceData}>
                  <CartesianGrid vertical={false} />
                  <XAxis dataKey="name" />
                  <YAxis dataKey="confidence" />
                  <ChartTooltip content={<ChartTooltipContent />} />
                  <Area
                    type="monotone"
                    dataKey="confidence"
                    stroke={`hsl(var(--chart-1))`}
                    fill={`hsl(var(--chart-1))`}
                  />
                </AreaChart>
              </ChartContainer>
            </CardContent>
          </Card>

          {/* Recent Requests Table */}
          <Card className="col-span-1 md:col-span-2">
            <CardHeader>
              <CardTitle className="text-2xl">Recent Requests</CardTitle>
            </CardHeader>
            <CardContent>
              <Table className="border-1">
                <TableHeader>
                  <TableRow>
                    <TableHead className="border-1 bg-white/5">
                      Request Type
                    </TableHead>
                    <TableHead className="border-1 bg-white/5">
                      Sub Request Type
                    </TableHead>
                    <TableHead className="border-1 bg-white/5">
                      Support Group
                    </TableHead>
                    <TableHead className="border-1 bg-white/5">
                      Confidence
                    </TableHead>
                    <TableHead className="border-1 bg-white/5">
                      Timestamp
                    </TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {data.map((req, index) => (
                    <TableRow key={'index-'+index}>
                      <TableCell className="border-1">
                        {req.request_type}
                      </TableCell>
                      <TableCell className="border-1">
                        {req.sub_request_type}
                      </TableCell>
                      <TableCell className="border-1">
                        {req.support_group}
                      </TableCell>
                      <TableCell className="border-1">
                        {(req.confidence * 100).toFixed(2)}%
                      </TableCell>
                      <TableCell>
                        {new Date(req.timestamp).toLocaleString()}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center min-h-screen">
          <LoadingSpinner size={50} />
          <div className="text-3xl">Loading data...</div>
        </div>
      )}
    </>
  );
};

export default Dashboard;
