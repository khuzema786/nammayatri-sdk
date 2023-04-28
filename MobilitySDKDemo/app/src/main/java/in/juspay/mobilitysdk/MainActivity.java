package in.juspay.mobilitysdk;

import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
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

    // block:start:back-press
    @Override
    public void onBackPressed() {
        if (hyperService != null && !hyperService.onBackPressed()) {
            super.onBackPressed();
        }
    }
    // block:end:back-press

    // block:start:on-activity-result
    @Override
    protected void onActivityResult(int requestCode, int resultCode, @Nullable Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        hyperService.onActivityResult(requestCode,resultCode,data);
    }
    // block:end:on-activity-result

    // block:start:on-permission-result
    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        hyperService.onRequestPermissionsResult(requestCode, permissions, grantResults);
    }
    // block:end:on-permission-result

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
            String key = "in.juspay.mobility";
            initiatePayload.put("requestId", UUID.randomUUID());
            initiatePayload.put("service", key);
            innerPayload.put("clientId", "<client_id>");
            innerPayload.put("merchantId", "<client_id>");
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
            innerPayload.put("clientId", "<client_id>");
            innerPayload.put("merchantId", "<client_id>");
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