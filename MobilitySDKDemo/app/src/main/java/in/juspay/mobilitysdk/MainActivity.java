package in.juspay.demosdk;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;

import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.widget.Button;

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
                if (jsonObject.optString("event").equals("initiate_result")) {
                    Log.i("MobilitySDK", "initiate successful");
                    hyperService.process(getProcessPayload());
                }
            }
        });
        // block:end:initiate-service
    }

    public void typesOfConstructor() {
        // block:start:constructor
        HyperServices hyperService = new HyperServices(this);
        // block:end:constructor

        // block:start:constructor-with-fragment-activity-and-view-group
        HyperServices hyperServiceWithFragment = new HyperServices(this, findViewById(R.id.container));
        // block:end:constructor-with-fragment-activity-and-view-group
    }

    public void typesOfInitiate() {
        // block:start:initiate-with-payload
        hyperService.initiate(getInitiatePayload(), new HyperPaymentsCallbackAdapter() {
            @Override
            public void onEvent(JSONObject jsonObject, JuspayResponseHandler juspayResponseHandler) {}});
        // block:end:initiate-with-payload

        // block:start:initiate-with-payload-and-fragment-activity
        hyperService.initiate(this,getInitiatePayload(), new HyperPaymentsCallbackAdapter() {
            @Override
            public void onEvent(JSONObject jsonObject, JuspayResponseHandler juspayResponseHandler) {}});
        // block:end:initiate-with-payload-and-fragment-activity

        // block:start:initiate-with-payload-fragment-and-view-group
        hyperService.initiate(this,findViewById(R.id.container),getInitiatePayload(), new HyperPaymentsCallbackAdapter() {
            @Override
            public void onEvent(JSONObject jsonObject, JuspayResponseHandler juspayResponseHandler) {}});
        // block:end:initiate-with-payload-fragment-and-view-group
    }


    public void typesOfProcess() {
        // block:start:process-with-payload
        hyperService.process(getProcessPayload());
        // block:end:process-with-payload

        // block:start:process-with-payload-fragment-and-view-group
        hyperService.process(this,findViewById(R.id.container),getProcessPayload());
        // block:end:process-with-payload-fragment-and-view-group

        // block:start:process-with-payload-and-fragment-activity
        hyperService.process(this,getProcessPayload());
        // block:end:process-with-payload-and-fragment-activity
    }


    // block:start:create-initiate-payload
    private JSONObject getInitiatePayload() {
        JSONObject innerPayload = new JSONObject();
        JSONObject initiatePayload = new JSONObject();
        try {
            String key = "in.yatri.consumer";
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
        String signature = "<signature>";
        try {
            String key = "in.yatri.consumer";
            initiatePayload.put("requestId", UUID.randomUUID());
            initiatePayload.put("service", key);
            innerPayload.put("clientId", "<client_id>");
            innerPayload.put("merchantId", "<client_id>");
            innerPayload.put("action", "process");
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

    // block:start:create-notification-payload
    private JSONObject getNotificationProcessPayload() {
        JSONObject innerPayload = new JSONObject();
        JSONObject processPayload = new JSONObject();
        try {
            String key = "in.yatri.consumer";
            processPayload.put("requestId", UUID.randomUUID());
            processPayload.put("service", key);
            innerPayload.put("clientId", "<client_id>");
            innerPayload.put("merchantId", "<client_id>");
            innerPayload.put("action", "process");
            innerPayload.put("service", key);
            innerPayload.put(PaymentConstants.ENV, "production");
            processPayload.put("action", "notification");
            JSONObject notification_content = new JSONObject();
            notification_content.put("type","<NOTIFICATION_TYPE>");
            innerPayload.put("notification_content",notification_content);
            processPayload.put(PaymentConstants.PAYLOAD, innerPayload);
        } catch (JSONException e) {
            e.printStackTrace();
        }
        return processPayload;
    }
    // block:end:create-notification-payload

    // block:start:create-deeplink-payload
    private JSONObject getDeepLinkProcessPayload() {
        JSONObject innerPayload = new JSONObject();
        JSONObject processPayload = new JSONObject();
        try {
            String key = "in.yatri.consumer";
            processPayload.put("requestId", UUID.randomUUID());
            processPayload.put("service", key);
            innerPayload.put("clientId", "<client_id>");
            innerPayload.put("merchantId", "<client_id>");
            innerPayload.put("action", "process");
            innerPayload.put("service", key);
            innerPayload.put("view_param", "<deeplink_key>");
            innerPayload.put(PaymentConstants.ENV, "production");
            processPayload.put(PaymentConstants.PAYLOAD, innerPayload);
        } catch (JSONException e) {
            e.printStackTrace();
        }
        return processPayload;
    }
    // block:end:create-deeplink-payload

    // block:start:create-direct-search-payload
    private JSONObject getDirectSearchProcessPayload() {
        JSONObject innerPayload = new JSONObject();
        JSONObject processPayload = new JSONObject();
        try {
            String key = "in.yatri.consumer";
            processPayload.put("requestId", UUID.randomUUID());
            processPayload.put("service", key);
            innerPayload.put("clientId", "<client_id>");
            innerPayload.put("merchantId", "<client_id>");
            innerPayload.put("action", "process");
            innerPayload.put("service", key);
            innerPayload.put("search_type","direct_search");
            JSONObject source = new JSONObject();
            source.put("lat",<lat>);
            source.put("lon",<lon>);
            source.put("name","<destination_name>");
            JSONObject dest = new JSONObject();
            dest.put("lat",<lat>);
            dest.put("lon",<lon>);
            dest.put("name","<place_name>");
            innerPayload.put("source", source);
            innerPayload.put("destination",dest);
            innerPayload.put(PaymentConstants.ENV, "production");
            processPayload.put(PaymentConstants.PAYLOAD, innerPayload);
        } catch (JSONException e) {
            e.printStackTrace();
        }
        return processPayload;
    }
    // block:end:create-direct-search-payload
}