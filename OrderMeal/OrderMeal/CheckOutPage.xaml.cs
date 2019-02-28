using System;
using System.Collections.Generic;
using System.Text;
using System.Net.Http;
using System.Threading.Tasks;
using Xamarin.Forms;
using Newtonsoft.Json;

namespace OrderMeal
{
    public class OrderInfo
    {
        public string email = "amanag96@gmail.com";
        public string name = "Aman Agrawal";
        //public string phone = "4088130108";
        public string street = "212 Test Drive";
        public string city = "San Jose";
        public string state = "CA";
        public string zipCode = "95139";
        public string totalAmount = "37.00";
        public bool paid = false;
        public string paymentType = "cash";
        public string deliveryTime = "5:00 PM";
        public string mealOption1 = "1";
        public string mealOption2 = "1";

    }
    public partial class CheckOutPage : ContentPage
    {
        OrderInfo currentOrder = new OrderInfo();

        public CheckOutPage(string optionOneMeals, string optionTwoMeals)
        {
            InitializeComponent();
            Option1Count.Text = optionOneMeals;
            Option2Count.Text = optionTwoMeals;
            var totalMealOptionOnePrice = Convert.ToInt32(optionOneMeals) * 20;
            var totalMealOptionTwoPrice = Convert.ToInt32(optionTwoMeals) * 24;
            var tax = (totalMealOptionOnePrice + totalMealOptionTwoPrice) * 0.09;
            var totalPrice = totalMealOptionOnePrice + totalMealOptionTwoPrice + tax;
            Tax.Text = "$" + tax.ToString();
            TotalPrice.Text = "$" + totalPrice.ToString();

            Auto_Fill("user_id", fullName);
            Auto_Fill("email", emailAddress);
            Auto_Fill("phone", phoneNumber);
            Auto_Fill("street", streetAddress);
            Auto_Fill("city", City);
            Auto_Fill("state", State);
            Auto_Fill("zip", zipCode);

            currentOrder.mealOption1 = Option1Count.Text;
            currentOrder.mealOption2 = Option2Count.Text;
            currentOrder.totalAmount = totalPrice.ToString();
        }

        void PayPal_Request(object sender, System.EventArgs e)
        {

        }

        void Handle_Clicked(object sender, System.EventArgs e)
        {
            DisplayAlert("Order Sent", "Thank you for your order. You can return to the previous screen to make another order.", "Done");
            if (fullName.Text != null)
            {
                Application.Current.Properties["user_id"] = fullName.Text;
                currentOrder.name = fullName.Text;
            }

            if (emailAddress.Text != null) 
            { 
                Application.Current.Properties["email"] = emailAddress.Text;
                currentOrder.email = emailAddress.Text;
            }
            if (phoneNumber.Text != null) { Application.Current.Properties["phone"] = phoneNumber.Text; }
            if (streetAddress.Text != null)
            {
                Application.Current.Properties["street"] = streetAddress.Text;
                currentOrder.street = streetAddress.Text;
            }
            if (City.Text != null)
            {
                Application.Current.Properties["city"] = City.Text;
                currentOrder.city = City.Text;
            }
            if (State.Text != null)
            {
                Application.Current.Properties["state"] = State.Text;
                currentOrder.state = State.Text;
            }
            if (zipCode.Text != null)
            {
                Application.Current.Properties["zip"] = zipCode.Text;
                currentOrder.zipCode = zipCode.Text;
            }
            Application.Current.SavePropertiesAsync();
            currentOrder.deliveryTime = deliveryTime.Time.ToString();
            
            Send(currentOrder);
        }

        void Auto_Fill(string key, Entry location)
        {
            if (Application.Current.Properties.ContainsKey(key) && Application.Current.Properties[key] != null)
            {
                location.Text = Application.Current.Properties[key].ToString();
            }
        }

        async Task Send(OrderInfo currentOrder)
        {
            var client = new HttpClient();

            var json = JsonConvert.SerializeObject(currentOrder);
            var content = new StringContent(json, Encoding.UTF8, "application/json");
            HttpResponseMessage response = null;

            string uri = "https://o5yv1ecpk1.execute-api.us-west-2.amazonaws.com/dev/api/v1/meal/order";
            response = await client.PostAsync(uri, content);
            var result = await response.Content.ReadAsStringAsync();
        }
    }
}
