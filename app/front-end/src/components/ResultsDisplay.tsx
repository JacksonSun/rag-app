import { useState, useCallback, useEffect } from "react";
import Grid from "@mui/material/Unstable_Grid2/Grid2";
import {
  Box,
  Card,
  CardContent,
  CardHeader,
  Divider,
  Typography,
  Zoom,
  Fab,
  Skeleton,
  Alert,
  Snackbar,
} from "@mui/material";
import { ResultSource, ExternalSource } from "@/app/api/models";
import SourceCard from "./SourceCard";
import ExternalSourceCard from "./ExternalSourceCard";
import KeyboardArrowUp from "@mui/icons-material/KeyboardArrowUp";
import useScrollTrigger from "@mui/material/useScrollTrigger";
import { ReactMarkdown } from "react-markdown/lib/react-markdown";
import rehypeRaw from "rehype-raw";

const ScrollTop = () => {
  const trigger = useScrollTrigger({
    threshold: 100,
  });

  const scrollToTop = useCallback(() => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  }, []);

  return (
    <Zoom in={trigger}>
      <Box
        role="presentation"
        sx={{
          position: "fixed",
          bottom: 32,
          right: 32,
          zIndex: 1,
        }}
      >
        <Fab
          onClick={scrollToTop}
          color="primary"
          size="medium"
          aria-label="scroll back to top"
          sx={{
            background: "#051C2C",
          }}
        >
          <KeyboardArrowUp />
        </Fab>
      </Box>
    </Zoom>
  );
};

interface ResultsDisplayProps {
  isFetching: boolean;
  query: string;
  sources: ResultSource[];
  result: string;
  externalSources: ExternalSource[];
}

export const ResultsDisplay: React.FC<ResultsDisplayProps> = ({
  isFetching,
  query,
  sources,
  result,
  externalSources,
}) => {
  const [alertOpen, setAlertOpen] = useState(false);
  const [errorMessage, setErrorMessage] = useState("Something went wrong!");

  const handleAlertClose = () => {
    setAlertOpen(false);
  };

  //   const handleError = (message: string) => {
  //     // setErrorMessage(message); TODO: wait for api error handling
  //     setAlertOpen(true);
  //   };

  return (
    <Box sx={{ width: 1, minHeight: "100vh" }}>
      <Snackbar
        anchorOrigin={{ vertical: "top", horizontal: "center" }}
        open={alertOpen}
        onClose={handleAlertClose}
        style={{ top: "18%" }}
      >
        <Alert
          onClose={handleAlertClose}
          severity="error"
          sx={{ width: "100%" }}
        >
          {errorMessage}
        </Alert>
      </Snackbar>
      {/* <AppBar
        position="sticky"
        sx={{
          top: "64px",
          background: "transparent",
          "box-shadow": "none !important",
        }}
      >
        <Toolbar>
          <Button
            variant="outlined"
            onClick={goBack}
            startIcon={<ArrowBackIcon />}
            sx={{ background: "white" }}
          >
            Ask New Question
          </Button>
        </Toolbar>
      </AppBar> */}
      <Card sx={{ mx: 2, mt: 2 }}>
        <CardHeader
          title={query}
          titleTypographyProps={{
            color: "white",
            fontWeight: 500,
            fontSize: "1rem",
          }}
          style={{
            background: "#051C2C",
          }}
        />
        <CardContent>
          <Grid container rowSpacing={3} columnSpacing={3}>
            {/* Summary */}
            <Grid xs={12}>
              {isFetching && result.length === 0 ? (
                <>
                  <Skeleton />
                  <Skeleton animation="wave" />
                  <Skeleton animation={false} />
                </>
              ) : (
                <ReactMarkdown
                  children={result.replace(
                    /\[\d+\]/g,
                    (match) =>
                      `<sup style="background: #D6EBFA ; color: #051C2C; outline: transparent solid 1px;">${
                        match.split(/\[([^\]]+)\]/g)[1]
                      }</sup> `
                  )}
                  rehypePlugins={[rehypeRaw] as any} // rehypeRaw is a plugin to render html inside markdown
                />
              )}
              <Divider variant="fullWidth" sx={{ my: 4 }} />
              {/* Source */}
              {isFetching && sources.length === 0 ? (
                <Skeleton variant="rectangular" width="100%">
                  <div style={{ paddingTop: "30%" }} />
                </Skeleton>
              ) : (
                sources.length > 0 && (
                  <div>
                    <Typography variant="body1" sx={{ my: 2, fontWeight: 500 }}>
                      Internal Sources
                    </Typography>
                    <Grid container columnSpacing={2} rowSpacing={2}>
                      {sources.map((source: ResultSource, index: number) => (
                        <SourceCard source={source} key={index} index={index} />
                      ))}
                    </Grid>
                    <Divider variant="fullWidth" sx={{ my: 2 }} />
                  </div>
                )
              )}
              {/* External Source */}
              {isFetching && externalSources.length === 0 ? (
                <Skeleton variant="rectangular" width="100%">
                  <div style={{ paddingTop: "30%" }} />
                </Skeleton>
              ) : (
                externalSources.length > 0 && (
                  <div>
                    <Typography variant="body1" sx={{ my: 4, fontWeight: 500 }}>
                      External Sources
                    </Typography>
                    <Grid container columnSpacing={2} rowSpacing={2}>
                      {externalSources.map(
                        (externalSource: ExternalSource, index: number) => (
                          <ExternalSourceCard
                            key={index}
                            externalSource={externalSource}
                            query={query}
                          />
                        )
                      )}
                    </Grid>
                  </div>
                )
              )}
            </Grid>
          </Grid>
        </CardContent>
      </Card>
      <ScrollTop />
    </Box>
  );
};
