import { useEffect, useState, KeyboardEvent, ChangeEvent } from "react";
import Grid from "@mui/material/Unstable_Grid2";
import SendIcon from "@mui/icons-material/Send";
import { TextField, InputAdornment, IconButton } from "@mui/material";
import SearchIcon from "@mui/icons-material/Search";

interface SearchBarProps {
  query: string;
  setQuery: (query: string) => void;
  search: () => void;
}

export const SearchBar: React.FC<SearchBarProps> = ({
  query,
  setQuery,
  search,
}) => {
  const [disableSubmitBtn, setDisableSubmitBtn] = useState(true);
  console.log("searchBar");

  // TODO - to be replaced
  //   const exampleQuestions = [
  //     "What would be the solution when EMI failure happens at 150 kHz?",
  //     "What is the solution of 3KW Surge issue?",
  //     "What would be the solution of PSFB MOS SCP stress issue?",
  //     "How to improve Titanium efficiency?",
  //   ];

  //   useEffect(() => {
  //     if (query.length === 0) setDisableSubmitBtn(true);
  //     else setDisableSubmitBtn(false);
  //   }, [query]);

  const handleChange = (event: ChangeEvent<HTMLTextAreaElement>) => {
    const target = event.target;
    setQuery(target.value);

    // Resize the textarea to fit the content
    target.style.height = "24px";
    const newHeight = target.scrollHeight;
    target.style.height = `${newHeight}px`;
  };

  const handleKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && !event.shiftKey) {
      search();
      event.preventDefault();
    }
  };

  return (
    <Grid xs={12}>
      <TextField
        value={query}
        onChange={(v: any) => handleChange(v)}
        onKeyDown={(v: any) => handleKeyDown(v)}
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <SearchIcon />
            </InputAdornment>
          ),
          endAdornment: (
            <InputAdornment position="end">
              <IconButton disabled={disableSubmitBtn} onClick={search}>
                <SendIcon color="primary" />
              </IconButton>
            </InputAdornment>
          ),
        }}
        multiline
        fullWidth
        rows={1}
        placeholder="Ask me anything on R&D to find the lesson learned in history..." // TODO: change placeholder
      />
    </Grid>
  );
};
