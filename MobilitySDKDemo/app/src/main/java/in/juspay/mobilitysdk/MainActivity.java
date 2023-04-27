package in.juspay.mobilitysdk;

import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;

import androidx.appcompat.app.AppCompatActivity;

import org.json.JSONException;
import org.json.JSONObject;

import java.util.UUID;

import in.juspay.hypersdk.core.PaymentConstants;
import in.juspay.hypersdk.data.JuspayResponseHandler;
import in.juspay.hypersdk.ui.HyperPaymentsCallbackAdapter;
import in.juspay.services.HyperServices;

public class MainActivity extends AppCompatActivity {
    private HyperServices hyperService;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        initMobilitySDK();
        Button button = findViewById(R.id.start);
        button.setOnClickListener(view -> {
            // block:start:process-call
            hyperService.process(getProcessPayload());
            // block:end:process-call
        });
    }



    private void initMobilitySDK() {
        // block:start:initiate-service
        hyperService = new HyperServices(this);
        hyperService.initiate(getInitiatePayload(), new HyperPaymentsCallbackAdapter() {
            @Override
            public void onEvent(JSONObject jsonObject, JuspayResponseHandler juspayResponseHandler) {
                // handle the whitelisted event
                try {
                    if (jsonObject.get("event") == "initiate_result") {
                        Log.i("MobilitySDK", "initiate successful");
                    }
                } catch (JSONException e) {
                    e.printStackTrace();
                }
            }
        });
        // block:end:initiate-service
    }

    // block:start:create-initiate-payload
    private JSONObject getInitiatePayload() {
        JSONObject innerPayload = new JSONObject();
        JSONObject initiatePayload = new JSONObject();
        try {
            String key = "in.juspay.hyperpay";
            initiatePayload.put("requestId", UUID.randomUUID());
            initiatePayload.put("service", key);
            innerPayload.put("clientId", "nammayatri");
            innerPayload.put("merchantId", "nammayatri");
            innerPayload.put("action", "initiate");
            innerPayload.put("service", key);
            innerPayload.put(PaymentConstants.ENV, "production");
            initiatePayload.put(PaymentConstants.PAYLOAD, innerPayload);
        } catch (JSONException e) {
            e.printStackTrace();
        }
        return initiatePayload;
    }
    // block:end:create-initiate-payload

    // block:start:create-process-payload
    private JSONObject getProcessPayload() {
        JSONObject innerPayload = new JSONObject();
        JSONObject initiatePayload = new JSONObject();
        JSONObject signatureAuthData = new JSONObject();
        String authData = "{\"mobileNumber\":\"9819xxxx90\",\"mobileCountryCode\":\"+91\",\"merchantId\":\"<MERCHANT_ID>\",\"timestamp\":\"2023-04-13T07:28:40+00:00\"}";
        String signature = "<SIGNATURE_KEY>";
        try {
            String key = "in.juspay.mobility";
            initiatePayload.put("requestId", UUID.randomUUID());
            initiatePayload.put("service", key);
            innerPayload.put("clientId", "nammayatri");
            innerPayload.put("merchantId", "nammayatri");
            innerPayload.put("action", "initiate");
            innerPayload.put("service", key);
            innerPayload.put(PaymentConstants.ENV, "production");
            signatureAuthData.put("signature", signature);
            signatureAuthData.put("authData", authData);
            innerPayload.put("signatureAuthData", signatureAuthData);
            initiatePayload.put(PaymentConstants.PAYLOAD, innerPayload);
        } catch (JSONException e) {
            e.printStackTrace();
        }
        return initiatePayload;
    }
    // block:end:create-process-payload
}