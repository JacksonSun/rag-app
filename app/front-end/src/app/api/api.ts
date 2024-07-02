const defaultConfig = {
  headers: {
    "Access-Control-Allow-Origin": "*",
    "Content-Type": "application/json",
  },
};

export const post = async (url: string, requestBody: any, config: any = {}) => {
  try {
    config = { ...defaultConfig, ...config };

    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_ENDPOINT}/` + url + "/", // local,
      {
        method: "POST",
        body: JSON.stringify(requestBody),
        ...config,
      }
    );
    return response;
  } catch (e) {
    console.log(e);
    // TODO: error
    throw { status: 401, message: "Bad Request" };
  }
};

export const uploadFileAPI = async (url: string, formData: any) => {
  try {
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_ENDPOINT}/` + url + "/", // local,
      {
        method: "POST",
        body: formData,
      }
    );

    return response;
  } catch (e) {
    console.log(e);
    // TODO: error
    throw { status: 401, message: "Bad Request" };
  }
};

export const get = async (
  url: string,
  params: any = null,
  config: any = {}
) => {
  try {
    config = { ...defaultConfig, ...config };

    let queryParams = "";
    if (params) {
      queryParams = "?" + new URLSearchParams(params).toString();
    }
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_ENDPOINT}/${url}/${queryParams}`, // local,
      {
        method: "GET",
        ...config,
      }
    );

    return response;
  } catch (e) {
    console.log(e);
    // TODO: error
    throw { status: 401, message: "Bad Request" };
  }
};
