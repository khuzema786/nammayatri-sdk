import http from 'k6/http';
import {sleep} from 'k6';

export const options = {
  stages: [
    { duration: '1m', target: 60 },
    { duration: '10m', target: 60 },
    { duration: '1m', target: 120 },
    { duration: '10m', target: 75 },
    { duration: '1m', target: 120 },
    { duration: '30m', target: 60 }
  ],
};

// export const options = {
//   stages: [
//     { duration: '1m', target: 60 },
//     { duration: '4m', target: 60 },
//   ],
// };

export default () => {
  http.post('https://api.sandbox.beckn.juspay.in/loadtest/bap/search');
  sleep(1);
};
