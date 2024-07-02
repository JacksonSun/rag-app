import { useState } from "react";
import Grid from "@mui/material/Unstable_Grid2/Grid2";
import {
  Divider,
  Link,
  Skeleton,
  Box,
  Typography,
  IconButton,
  Tooltip,
} from "@mui/material";
import { ExternalSource, WebSummaryRequest } from "@/app/api/models";
import EmojiObjectsOutlinedIcon from "@mui/icons-material/EmojiObjectsOutlined";
import { post } from "@/app/api/api";

export default function ExternalSourceCard({
  externalSource,
  query,
}: {
  externalSource: ExternalSource;
  query: string;
}) {
  const [loading, setLoading] = useState(false);
  const [summary, setSummary] = useState("");

  const streamSummary = async (response: any) => {
    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    let done = false;
    let result = "";

    while (!done) {
      const { value, done: doneReading } = await reader.read();
      done = doneReading;
      const chunkValue = decoder.decode(value);

      result += chunkValue;
      setSummary(result + (done ? "" : "▌"));
    }
  };

  const handleGenerateSummary = () => {
    setLoading(true);
    setSummary("");
    const req: WebSummaryRequest = {
      query: query,
      url: externalSource.url,
    };
    post("webpage_summary", req).then((response: any) => {
      if (response.ok) {
        streamSummary(response).then(() => {
          setLoading(false);
        });
      } else {
        throw response;
      }
    });
  };

  return (
    <Grid
      md={12}
      sx={{ width: 0.5, padding: "0 20px 0 20px", marginBottom: "16px" }}
    >
      <Grid container justifyContent={"space-between"}>
        <Link
          href={externalSource.url}
          target="_blank"
          sx={{
            color: "#2582EE",
            textDecorationColor: "#2582EE",
            fontWeight: 500,
            paddingBottom: "8px",
          }}
        >
          {externalSource.title}
        </Link>
        <Tooltip title="Generate Summary" arrow>
          <IconButton
            sx={{
              background: "#e8e8e8",
              borderRadius: "4px",
              width: "30px",
              height: "26px",
            }}
            disabled={loading}
          >
            <EmojiObjectsOutlinedIcon
              onClick={handleGenerateSummary}
              sx={{ width: "14px", height: "14px" }}
            />
          </IconButton>
        </Tooltip>
      </Grid>
      <div
        style={{ fontSize: "14px", color: "#6c6c6c", paddingBottom: "12px" }}
        dangerouslySetInnerHTML={{ __html: externalSource.snippet }}
      />
      {/* Summary */}
      {loading ? (
        <>
          <Skeleton />
          <Skeleton animation="wave" />
          <Skeleton animation={false} />
        </>
      ) : (
        summary.length > 0 && (
          <Box>
            <Typography
              sx={{
                fontWeight: "500",
                color: "#333333",
                fontSize: "14px",
                paddingBottom: "6px",
              }}
            >
              AI Summary
            </Typography>
            <Box
              sx={{
                background: "#D6EBFA",
                padding: "12px",
                color: "#051C2C",
                fontSize: "14px",
              }}
            >
              {summary}
            </Box>
          </Box>
        )
      )}
      <Divider sx={{ paddingTop: "12px" }}></Divider>
    </Grid>
  );
}
