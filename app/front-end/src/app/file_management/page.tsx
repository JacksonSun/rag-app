"use client";
import { useState, useEffect } from "react";
import Box from "@mui/material/Box";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TablePagination from "@mui/material/TablePagination";
import TableRow from "@mui/material/TableRow";
import IconButton from "@mui/material/IconButton";
import FirstPageIcon from "@mui/icons-material/FirstPage";
import KeyboardArrowLeft from "@mui/icons-material/KeyboardArrowLeft";
import KeyboardArrowRight from "@mui/icons-material/KeyboardArrowRight";
import LastPageIcon from "@mui/icons-material/LastPage";
import {
  Alert,
  AlertColor,
  Button,
  Skeleton,
  Snackbar,
  TableFooter,
  Typography,
  useTheme,
} from "@mui/material";
import EditIcon from "@mui/icons-material/Edit";
import FileUploadIcon from "@mui/icons-material/FileUpload";
import Dialog from "@mui/material/Dialog";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import DialogActions from "@mui/material/DialogActions";
import TextField from "@mui/material/TextField";
import Grid from "@mui/material/Grid";
import EmojiObjectsIcon from "@mui/icons-material/EmojiObjects";
import { get, post, uploadFileAPI } from "../api/api";
import { LoadingButton } from "@mui/lab";

interface FileObject {
  docName: string;
  summary: string;
  lastModifiedDate: string | null; // 'YYYY-MM-DD HH:MM:SS'
}

type Order = "asc" | "desc";

interface HeadCell {
  disablePadding: boolean;
  id?: keyof FileObject;
  label?: string;
  numeric: boolean;
}

const headCells: readonly HeadCell[] = [
  {
    id: "docName",
    numeric: false,
    disablePadding: true,
    label: "File Name",
  },
  {
    id: "summary",
    numeric: false,
    disablePadding: true,
    label: "Summary",
  },
  {
    id: "lastModifiedDate",
    numeric: false,
    disablePadding: true,
    label: "Modified Date",
  },
  {
    numeric: false,
    disablePadding: true,
  },
];

interface TablePaginationActionsProps {
  count: number;
  page: number;
  rowsPerPage: number;
  onPageChange: (
    event: React.MouseEvent<HTMLButtonElement>,
    newPage: number
  ) => void;
}

/**
 * Table pagination action
 * @param {TablePaginationActionsProps} props - Brief description of the parameter here. Note: For other notations of data types, please refer to JSDocs: DataTypes command.
 * @return {ReturnValueDataTypeHere} Brief description of the returning value here.
 */
const TablePaginationActions = (props: TablePaginationActionsProps) => {
  const theme = useTheme();
  const { count, page, rowsPerPage, onPageChange } = props;

  const handleFirstPageButtonClick = (
    event: React.MouseEvent<HTMLButtonElement>
  ) => {
    onPageChange(event, 0);
  };

  const handleBackButtonClick = (
    event: React.MouseEvent<HTMLButtonElement>
  ) => {
    onPageChange(event, page - 1);
  };

  const handleNextButtonClick = (
    event: React.MouseEvent<HTMLButtonElement>
  ) => {
    onPageChange(event, page + 1);
  };

  const handleLastPageButtonClick = (
    event: React.MouseEvent<HTMLButtonElement>
  ) => {
    onPageChange(event, Math.max(0, Math.ceil(count / rowsPerPage) - 1));
  };

  return (
    <Box sx={{ flexShrink: 0, ml: 2.5 }}>
      <IconButton
        onClick={handleFirstPageButtonClick}
        disabled={page === 0}
        aria-label="first page"
      >
        {theme.direction === "rtl" ? <LastPageIcon /> : <FirstPageIcon />}
      </IconButton>
      <IconButton
        onClick={handleBackButtonClick}
        disabled={page === 0}
        aria-label="previous page"
      >
        {theme.direction === "rtl" ? (
          <KeyboardArrowRight />
        ) : (
          <KeyboardArrowLeft />
        )}
      </IconButton>
      <IconButton
        onClick={handleNextButtonClick}
        disabled={page >= Math.ceil(count / rowsPerPage) - 1}
        aria-label="next page"
      >
        {theme.direction === "rtl" ? (
          <KeyboardArrowLeft />
        ) : (
          <KeyboardArrowRight />
        )}
      </IconButton>
      <IconButton
        onClick={handleLastPageButtonClick}
        disabled={page >= Math.ceil(count / rowsPerPage) - 1}
        aria-label="last page"
      >
        {theme.direction === "rtl" ? <FirstPageIcon /> : <LastPageIcon />}
      </IconButton>
    </Box>
  );
};

export default function FileManagementPage() {
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10); // rowsPerPage default to 10
  const [open, setOpen] = useState(false);
  const [filename, setFilename] = useState<string>("");
  const [summary, setSummary] = useState<string>("");
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [genSummaryLoading, setGenSummaryLoading] = useState<boolean>(false);
  const [submitLoading, setSubmitLoading] = useState<boolean>(false);
  const [fileList, setFileList] = useState<FileObject[]>([]);
  const [alertOn, setAlertOn] = useState<boolean>(false);
  const [alertMessage, setAlertMessage] = useState<String>("");
  const [alertType, setAlertType] = useState<AlertColor>("success");

  useEffect(() => {
    if (fileList.length === 0) {
      getFileList();
    }
  }, []);

  const handleClose = () => {
    setOpen(false);
    setFilename("");
    setSummary("");
    setFile(null);
  };

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  /**
   * Handle alert on close.
   * @param // None
   * @return // None
   */
  const handleAlertClose = () => {
    setAlertOn(false);
  };

  /**
   * Get list of files uploaded by the given user.
   * @param {ParamDataTypeHere} params - Brief description of the parameter here. Note: For other notations of data types, please refer to JSDocs: DataTypes command.
   * @return None
   */
  const getFileList = () => {
    console.log("get file list");
    get("get_file_list")
      .then((response: any) => {
        if (response.ok) {
          response.json().then((data: any) => {
            const files: FileObject[] = data.file_list.map(
              (file: any, index: number) => ({
                id: index,
                docName: file.title,
                summary: file.summary,
                lastModifiedDate: file.created_at.split(" ")[0],
              })
            );
            setFileList(files);
          });
        } else {
          throw response;
        }
      })
      .catch((e) => {
        console.log("error= ", e); // TODO
      });
  };

  /**
   * Temporary upload file
   * @param {ChangeEvent<HTMLInputElement>} event - Brief description of the parameter here. Note: For other notations of data types, please refer to JSDocs: DataTypes command.
   * @return {ReturnValueDataTypeHere} Brief description of the returning value here.
   */
  const handleTempFileUpload = async (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    setLoading(true);
    event.preventDefault();
    setOpen(true);

    if (event.target.files !== null && event.target.files.length === 1) {
      const f: File = event.target.files[0];
      setFile(f);
      setFilename(f.name);
    } else {
      return; // TODO error handling
    }
    event.target.value = "";
    setLoading(false);
  };

  const [blinking, setBlinking] = useState<boolean>(false);
  useEffect(() => {
    if (blinking) setSummary(genSummaryLoading ? "Generating..." : " ");
  }, [blinking]);

  /**
   * Web stream texting
   * @param {any} response - Brief description of the parameter here. Note: For other notations of data types, please refer to JSDocs: DataTypes command.
   */
  const streamSummary = async (response: any) => {
    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    let done = false;
    let result = "";
    while (!done) {
      const { value, done: doneReading } = await reader.read();
      setBlinking(false);
      done = doneReading;
      const chunkValue = decoder.decode(value);

      result += chunkValue;
      setSummary(result + (done ? "" : "▌"));
    }
    setGenSummaryLoading(false);
  };

  /**
   * Call API to generate summary using GenAI
   * @param  // None
   * @return // None
   */
  const generateSummary = async () => {
    setGenSummaryLoading(true);
    setBlinking(true);
    const formData = new FormData();
    if (file) {
      formData.append("file", file);
      uploadFileAPI("generate_file_summary", formData)
        .then((response: any) => {
          if (response.ok) {
            streamSummary(response);
          } else {
            throw new Error(response.detail);
          }
        })
        .catch((error) => {
          console.error(error); // TODO
          setGenSummaryLoading(false);
        });
    }
  };

  /**
   * Upload file and metadata
   * @param // None
   * @return// None
   */
  const handleSubmit = () => {
    setSubmitLoading(true);
    const formData = new FormData();

    if (file) formData.append("file", file);
    else formData.append("file", new Blob([]));

    const fileMetadata = {
      title: filename,
      summary: summary,
      url: "/data/" + filename,
    };
    formData.append("metadata", JSON.stringify(fileMetadata));

    uploadFileAPI("upsert-file", formData)
      .then((response) => {
        if (response.ok) {
          setAlertMessage("File was uploaded successfully.");
          setAlertType("success");
          setAlertOn(true);
          getFileList(); // TODO: pass in user id
        } else {
          throw response;
        }
      })
      .catch((e) => {
        setAlertMessage("Oops, something went wrong!");
        setAlertType("error");
        setAlertOn(true);
        console.log("e"); // TODO error
      })
      .finally(() => {
        setOpen(false);
        setFilename("");
        setSummary("");
        setSubmitLoading(false);
      });
  };

  return (
    <Box>
      {/* Alert  */}
      <Snackbar
        anchorOrigin={{ vertical: "top", horizontal: "center" }}
        open={alertOn}
        autoHideDuration={6000}
        onClose={handleAlertClose}
        style={{ top: "10%" }}
      >
        <Alert
          onClose={handleAlertClose}
          severity={alertType}
          sx={{ width: "100%" }}
        >
          {alertMessage}
        </Alert>
      </Snackbar>
      {/* File upload */}
      <Box
        sx={{
          display: "flex",
          justifyContent: "end",
          alignItems: "right",
          px: 5,
          py: 2,
        }}
      >
        {/* Button to upload file */}
        <label htmlFor="upload-file">
          <Button
            variant="outlined"
            startIcon={<FileUploadIcon />}
            component="span"
            sx={{
              bgcolor: "primary.main",
              color: "primary.contrastText",
              "&:hover": {
                bgcolor: "primary.dark",
              },
            }}
          >
            Upload File
            <input
              id="upload-file"
              name="upload-file"
              hidden
              accept=".pdf,.ppt,.pptx,.doc,.docx"
              type="file"
              onChange={handleTempFileUpload}
            />
          </Button>
        </label>
        {/* Pop up dialog for file uploading */}
        <Dialog open={open} fullWidth maxWidth="md">
          <DialogTitle>UPLOAD THE FILE</DialogTitle>
          {loading ? (
            <DialogContent>
              <Skeleton variant="rectangular" width="100%">
                <div style={{ paddingTop: "30%" }} />
              </Skeleton>
            </DialogContent>
          ) : (
            <>
              <DialogContent>
                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <Typography variant="caption">File name</Typography>
                    <Typography
                      variant="body2"
                      sx={{
                        whiteSpace: "normal",
                        wordWrap: "break-word",
                        textDecoration: "underline",
                      }}
                    >
                      {filename}
                    </Typography>
                  </Grid>
                  <Grid
                    item
                    xs={12}
                    sx={{
                      display: "flex",
                      justifyContent: "end",
                      alignItems: "right",
                    }}
                  >
                    <LoadingButton
                      variant="outlined"
                      startIcon={<EmojiObjectsIcon />}
                      loading={genSummaryLoading}
                      sx={{
                        bgcolor:
                          genSummaryLoading || blinking
                            ? "grey.500"
                            : "primary.main",
                        color:
                          genSummaryLoading || blinking
                            ? "grey.300"
                            : "primary.contrastText",
                        "&:hover": {
                          bgcolor:
                            genSummaryLoading || blinking
                              ? "grey.700"
                              : "primary.dark",
                        },
                      }}
                      disabled={blinking || genSummaryLoading}
                      onClick={generateSummary}
                    >
                      Generate by AI
                    </LoadingButton>
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      id="standard-multiline-static"
                      label="Summary"
                      placeholder="Please write a summary about your document or use Genearte By AI to help you populate a summary"
                      fullWidth
                      multiline
                      rows={10}
                      variant="outlined"
                      value={summary}
                      disabled={blinking || genSummaryLoading}
                      onChange={(e) => {
                        setSummary(e.target.value);
                      }}
                      autoFocus
                    />
                  </Grid>
                </Grid>
              </DialogContent>
              <DialogActions>
                <LoadingButton
                  loading={submitLoading}
                  onClick={handleClose}
                  disabled={genSummaryLoading}
                >
                  Cancel
                </LoadingButton>
                <LoadingButton
                  loading={submitLoading}
                  onClick={handleSubmit}
                  disabled={genSummaryLoading}
                >
                  Upload
                </LoadingButton>
              </DialogActions>
            </>
          )}
        </Dialog>
      </Box>
      {/* Talbe for list of files */}
      <Box sx={{ mx: 4 }}>
        <TableContainer sx={{ p: 2 }}>
          <Table aria-labelledby="tableTitle" size="small">
            <TableHead>
              <TableRow>
                {headCells.map((headCell, index) => (
                  <TableCell
                    key={index}
                    align="left"
                    padding={headCell.disablePadding ? "none" : "normal"}
                  >
                    {headCell.label}
                  </TableCell>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {fileList.map((row, index) => (
                <TableRow
                  hover
                  key={index}
                  role="checkbox"
                  tabIndex={-1}
                  sx={{ cursor: "pointer" }}
                >
                  <TableCell
                    align="left"
                    sx={{ width: "15%", maxWidth: "250px", pl: 0 }}
                    style={{
                      whiteSpace: "normal",
                      wordWrap: "break-word",
                    }}
                  >
                    {row.docName}
                  </TableCell>
                  <TableCell align="left" sx={{ width: "60%", pl: 0 }}>
                    {row.summary}
                  </TableCell>
                  <TableCell align="left" sx={{ width: "10%", pl: 0 }}>
                    {row.lastModifiedDate}
                  </TableCell>
                  <TableCell sx={{ width: "5%", pr: 0 }}>
                    <IconButton
                      aria-label="edit"
                      size="small"
                      color="primary"
                      onClick={() => {
                        setOpen(true);
                        setFilename(row.docName);
                        setSummary(row.summary);
                      }}
                    >
                      <EditIcon fontSize="inherit" />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
            <TableFooter>
              <TableRow>
                <TablePagination
                  rowsPerPageOptions={[5, 10, 25]}
                  count={fileList.length}
                  rowsPerPage={rowsPerPage}
                  page={page}
                  onPageChange={handleChangePage}
                  onRowsPerPageChange={handleChangeRowsPerPage}
                  ActionsComponent={TablePaginationActions}
                />
              </TableRow>
            </TableFooter>
          </Table>
        </TableContainer>
      </Box>
    </Box>
  );
}
