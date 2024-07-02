"use client";

import { useState } from "react";
import { Box, Typography } from "@mui/material";
import Grid from "@mui/material/Unstable_Grid2";
import { ExternalSource, PromptRequest, ResultSource } from "./api/models";
import { SearchBar } from "@/components/SearchBar";
import { ResultsDisplay } from "@/components/ResultsDisplay";
import { post } from "./api/api";

export default function HomePage() {
  const [query, setQuery] = useState("");
  const [isFetching, setIsFetching] = useState(false);
  const [sources, setSources] = useState<ResultSource[]>([]);
  const [result, setResult] = useState("");
  const [externalSources, setExternalSources] = useState<ExternalSource[]>([]);
  const [initState, setInitState] = useState(true);

  const streamResult = async (response: any) => {
    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    let done = false;
    let result = "";

    while (!done) {
      const { value, done: doneReading } = await reader.read();
      done = doneReading;
      let chunkValue = decoder.decode(value);

      result += chunkValue;
      setResult(result + (done ? "" : "▌"));
    }
  };

  const resetState = () => {
    setIsFetching(true);
    setSources([]);
    setResult("");
    setExternalSources([]);
  };

  const search = async () => {
    setInitState(false);
    resetState();
    // setDisableSubmitBtn(true);
    const req: PromptRequest = {
      query: query,
    };
    // 1. call results
    post("get_relevant", req)
      .then((response: any) => {
        if (response.ok) {
          response.json().then((data: any) => {
            setSources(data);

            // 2. call summary
            post("summary", req).then((response: any) => {
              if (response.ok) {
                streamResult(response).then(() => {
                  setIsFetching(false);
                });
              } else {
                throw response;
              }
            });

            post("search_external", req).then((response: any) => {
              if (response.ok) {
                response.json().then((data: any) => {
                  setExternalSources(data);
                  setIsFetching(false);
                });
              } else {
                throw response;
              }
            });
          });
        } else {
          throw response;
        }
      })
      .catch((e) => {
        // handleError("error"); // TODO error handling with backend
        console.log(e);
      });
  };

  return (
    <Box sx={{ width: 1, mt: 2 }}>
      <Grid
        container
        rowSpacing={3}
        columnSpacing={3}
        xs={10}
        xsOffset={1}
        justifyContent="center"
      >
        {/* Search Bar */}
        {initState ? (
          <Typography
            variant="h4"
            sx={{ fontWeight: 500, marginTop: 25, marginBottom: 2 }}
          >
            Ask a question
          </Typography>
        ) : (
          <></>
        )}
        <SearchBar query={query} setQuery={setQuery} search={search} />
        {/* Result Display */}
        {isFetching || result.length > 0 ? (
          <ResultsDisplay
            isFetching={isFetching}
            query={query}
            sources={sources}
            result={result}
            externalSources={externalSources}
          />
        ) : (
          <></>
        )}
      </Grid>
    </Box>
  );
}
