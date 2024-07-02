import { useEffect, useState } from "react";
import Grid from "@mui/material/Unstable_Grid2/Grid2";
import {
  Avatar,
  Box,
  Card,
  CardContent,
  Divider,
  IconButton,
  Stack,
  Tooltip,
  Typography,
} from "@mui/material";
import { ResultSource } from "@/app/api/models";
import DocViewer from "./DocViewer";
import ThumbUpOffAltIcon from "@mui/icons-material/ThumbUpOffAlt";
import ThumbDownOffAltIcon from "@mui/icons-material/ThumbDownOffAlt";

export default function SourceCard({
  source,
  index,
}: {
  source: ResultSource;
  index: number;
}) {
  const [showMore, setShowMore] = useState<boolean>(false);
  const [irrelavant, setIrrelavant] = useState(false);
  const [good, setGood] = useState(false);

  const handleShowMore = () => {
    setShowMore(!showMore);
  };

  const handleIrrelavant = () => {
    if (good) {
      setGood(!good);
    }
    setIrrelavant(!irrelavant);
  };

  const handleGood = () => {
    if (irrelavant) {
      setIrrelavant(!irrelavant);
    }
    setGood(!good);
  };

  return (
    <Grid md={12} sx={{ width: 0.5 }}>
      <Card>
        <CardContent>
          {/* Filename */}
          <Box
            display="flex"
            alignItems="center"
            justifyContent="space-between"
          >
            <Box sx={{ display: "flex", alignItems: "center" }}>
              <Avatar
                sx={{
                  bgcolor: "#D6EBFA",
                  color: "#051C2C",
                  width: 22,
                  height: 22,
                  fontSize: "0.8rem",
                }}
              >
                {index + 1}
              </Avatar>
              <DocViewer source={source} />
            </Box>
            <Stack direction="row" alignItems="center" spacing={0.5}>
              <Tooltip title="Good" arrow>
                <IconButton
                  sx={{
                    background: "#eeeeee",
                    borderRadius: "4px",
                    width: "30px",
                    height: "26px",
                    color: good ? "#00A9F4" : "",
                  }}
                >
                  <ThumbUpOffAltIcon
                    onClick={handleGood}
                    sx={{ width: "14px", height: "14px" }}
                  />
                </IconButton>
              </Tooltip>
              <Tooltip title="Irrelavent" arrow>
                <IconButton
                  sx={{
                    background: "#eeeeee",
                    borderRadius: "4px",
                    width: "30px",
                    height: "26px",
                    color: irrelavant ? "#ff0000" : "",
                  }}
                >
                  <ThumbDownOffAltIcon
                    onClick={handleIrrelavant}
                    sx={{ width: "14px", height: "14px" }}
                  />
                </IconButton>
              </Tooltip>
            </Stack>
          </Box>
          {/* Summary */}
          <Typography
            variant="body1"
            component="div"
            sx={{ mt: 1.5, mb: 0 }}
            style={{
              lineHeight: "1.2em",
              maxHeight: showMore ? "none" : "3.6em",
              overflow: "hidden",
              textOverflow: "ellipsis",
            }}
          >
            {/* TODO! */}
            {source.text.replace(/\uFFFD/g, "")}
          </Typography>
          {!showMore && "... "}
          <Typography
            variant="caption"
            onClick={handleShowMore}
            sx={{
              cursor: "pointer",
              textDecoration: "underline",
            }}
          >
            {!showMore ? "Show More" : "Show Less"}
          </Typography>
          <Divider sx={{ my: 2 }} />
          {/* Contact Person */}
          <Typography variant="body2" sx={{ my: 0.5 }}>
            <b>Contact Person: </b>
            {source.metadata.author}
          </Typography>
        </CardContent>
      </Card>
    </Grid>
  );
}
